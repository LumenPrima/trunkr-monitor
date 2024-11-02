from rich.console import Console
from rich.live import Live
from rich.layout import Layout
import signal
import sys
from database import DatabaseManager
from tables import TableManager
import argparse
from datetime import datetime
import threading
import time

class CallMonitor:
    def __init__(self, interactive=True):
        self.console = Console()
        self.db_manager = DatabaseManager()
        self.table_manager = TableManager()
        self.running = True
        self.live = None
        self.interactive = interactive
        self.layout = None
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Data cache
        self._active_calls = []
        self._recent_calls = []
        self._recent_units = []
        
        # Lock for thread-safe data updates
        self.data_lock = threading.Lock()
        
        # Register for database updates
        self.db_manager.register_callback(self.handle_update)

    def create_layout(self):
        """Create layout with three tables"""
        layout = Layout()
        
        # Get terminal height
        terminal_height = self.console.height
        
        # Calculate heights - reserve 20% for active calls
        active_height = 20
        remaining_height = terminal_height - active_height
        
        # Split horizontally first
        layout.split_row(
            Layout(name="left", size=45),
            Layout(name="recent")
        )
        
        # Split left side vertically with calculated ratio
        layout["left"].split_column(
            Layout(name="active", size=active_height),
            Layout(name="units", size=remaining_height)
        )
        
        # Set minimum sizes
        layout["left"].minimum_size = 50
        layout["recent"].minimum_size = 60
        
        return layout

    def _fetch_data(self):
        """Fetch data from database manager"""
        with self.data_lock:
            self._active_calls = self.db_manager.get_active_calls()
            self._recent_calls = self.db_manager.get_recent_calls()
            self._recent_units = self.db_manager.get_recent_units()

    def update_display(self):
        """Update all tables"""
        # Fetch latest data
        self._fetch_data()
        
        # Create layout if needed
        if not self.layout:
            self.layout = self.create_layout()
        
        try:
            # Create tables with cached data
            active_table = self.table_manager.create_active_calls_table(
                self._active_calls, self._recent_calls
            )
            units_table = self.table_manager.create_units_table(self._recent_units)
            recent_table = self.table_manager.create_recent_calls_table(self._recent_calls)
            
            # Update layout with new tables
            self.layout["left"]["active"].update(active_table)
            self.layout["left"]["units"].update(units_table)
            self.layout["recent"].update(recent_table)
            
            return self.layout
            
        except Exception as e:
            self.console.print(f"[red]Error creating tables: {str(e)}")
            return self.layout

    def handle_update(self):
        """Handle database updates"""
        if self.interactive and self.live:
            try:
                # Update the display without holding the lock
                self.live.update(self.update_display())
            except Exception as e:
                self.console.print(f"[red]Error updating display: {str(e)}")

    def print_updates(self):
        """Print updates in non-interactive mode"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.console.print(f"\n\n{'='*35} Update at {timestamp} {'='*35}")
        self.console.print(self.update_display())

    def check_health(self):
        """Check health of database connections and threads"""
        try:
            # Check thread status
            thread_status = self.db_manager.check_thread_status()
            
            # Check if we're getting fresh data
            latest_unit = self.db_manager.db.units_metadata.find_one(
                sort=[("timestamp", -1)]
            )
            
            now = int(time.time())
            data_fresh = latest_unit and (now - latest_unit['timestamp']) < 10
            
            health_status = {
                'threads': thread_status,
                'data_fresh': data_fresh,
                'last_update': latest_unit['timestamp'] if latest_unit else None
            }
            
            return health_status
        except Exception as e:
            return {'error': str(e)}

    def run(self):
        """Main monitoring loop"""
        if self.interactive:
            self.console.clear()
            self.console.print("\n🎙️ Real-time Radio Call Monitor - Press Ctrl+C to exit\n")
            
            # Create initial display
            initial_display = self.update_display()
            
            with Live(
                initial_display,
                refresh_per_second=10,  # Higher refresh rate
                vertical_overflow="visible",
                auto_refresh=True,
                transient=True  # Prevent screen artifacts
            ) as live:
                self.live = live
                while self.running:
                    try:
                        # Force refresh every 100ms
                        self.live.refresh()
                        time.sleep(0.1)
                    except (KeyboardInterrupt, SystemExit):
                        break
                    except Exception as e:
                        self.console.print(f"[red]Error in main loop: {str(e)}")
                        break
        else:
            # Non-interactive mode remains unchanged
            self.console.print("\n🎙️ Real-time Radio Call Monitor (Non-interactive Mode) - Press Ctrl+C to exit\n")
            self.print_updates()
            while self.running:
                try:
                    signal.pause()
                except (KeyboardInterrupt, SystemExit):
                    break
                except Exception as e:
                    self.console.print(f"[red]Error in main loop: {str(e)}")
                    break

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C signal"""
        self.running = False
        if self.live:
            self.live.stop()
        self.console.print("\n👋 Monitoring stopped")
        sys.exit(0)

def parse_args():
    parser = argparse.ArgumentParser(description='Radio Call Monitor')
    parser.add_argument('--non-interactive', action='store_true', 
                      help='Run in non-interactive mode (append output instead of updating)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    monitor = CallMonitor(interactive=not args.non_interactive)
    monitor.run()
