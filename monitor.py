from rich.console import Console
from rich.live import Live
from rich.layout import Layout
import signal
import sys
import time
from database import DatabaseManager
from tables import TableManager

class CallMonitor:
    def __init__(self):
        self.console = Console()
        self.db_manager = DatabaseManager()
        self.table_manager = TableManager()
        self.running = True
        self.live = None
        signal.signal(signal.SIGINT, self.signal_handler)

    def create_layout(self):
        """Create side-by-side layout"""
        layout = Layout()
        layout.split_row(
            Layout(name="active"),
            Layout(name="recent")
        )
        return layout

    def update_display(self):
        """Update both tables"""
        active_calls = self.db_manager.get_active_calls()
        recent_calls = self.db_manager.get_recent_calls()
        
        layout = self.create_layout()
        layout["active"].update(self.table_manager.create_active_calls_table(active_calls))
        layout["recent"].update(self.table_manager.create_recent_calls_table(recent_calls))
        
        return layout

    def run(self):
        """Main monitoring loop"""
        self.console.clear()
        self.console.print("\n🎙️ Real-time Radio Call Monitor - Press Ctrl+C to exit\n")
        
        with Live(self.update_display(), refresh_per_second=2) as live:
            self.live = live
            while self.running:
                try:
                    self.live.update(self.update_display())
                    time.sleep(0.5)
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

if __name__ == "__main__":
    monitor = CallMonitor()
    monitor.run()
