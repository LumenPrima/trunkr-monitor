#!/usr/bin/env python3

from rich.console import Console
from rich.live import Live
from rich.table import Table
import signal
import sys
from database import DatabaseManager
import argparse
from datetime import datetime
import threading
import time
import pytz
import os
from config import TIMEZONE, TIME_FORMAT

class TalkgroupMonitor:
    def __init__(self, talkgroup, interactive=True):
        self.console = Console()
        self.db_manager = DatabaseManager()
        self.running = True
        self.live = None
        self.interactive = interactive
        self.talkgroup = str(talkgroup)
        self.timezone = pytz.timezone(TIMEZONE)
        
        # Get terminal height and calculate max rows
        # Account for headers, borders, and status message
        terminal_height = os.get_terminal_size().lines
        self.max_display_rows = max(5, terminal_height - 6)
        
        # Get talkgroup info
        tg_info = self.db_manager.db.talkgroups_list.find_one(
            {"Decimal": int(talkgroup)}
        )
        
        if not tg_info:
            self.console.print(f"[red]Error: Talkgroup {talkgroup} not found in database")
            sys.exit(1)
            
        self.tg_description = tg_info.get('Description', '')
        
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Data cache
        self._active_calls = []
        self._recent_calls = []
        
        # Lock for thread-safe data updates
        self.data_lock = threading.Lock()
        
        # Register for database updates
        self.db_manager.register_callback(self.handle_update)

    def _fetch_data(self):
        """Fetch data specific to the monitored talkgroup"""
        with self.data_lock:
            now = int(time.time())
            
            # Get active calls from units_metadata for this talkgroup
            active_units = list(self.db_manager.db.units_metadata.find(
                {
                    "talkgroup": int(self.talkgroup),
                    "action": "call",
                    "timestamp": {"$gte": now - 30}  # Last 30 seconds
                },
                sort=[("timestamp", -1)]
            ))
            
            self._active_calls = active_units
            
            # Calculate how many historical calls to fetch based on available space
            remaining_rows = self.max_display_rows - len(active_units)
            
            # Get historical calls with transcriptions
            self._recent_calls = list(self.db_manager.db.calls_metadata.find(
                {"talkgroup": int(self.talkgroup)},
                sort=[("start_time", -1)]
            ).limit(remaining_rows))

    def create_table(self):
        """Create a table showing talkgroup activity"""
        table = Table(show_header=True, show_lines=True)
        
        # Match screenshot format
        table.add_column("Time", style="cyan", width=12)
        table.add_column("Duration", style="magenta", width=6)
        table.add_column("Unit", style="blue", width=12)
        table.add_column("Description", style="yellow")
        table.add_column("Message", style="white", overflow="fold")
        
        now = int(time.time())
        
        # Add active calls
        for call in self._active_calls:
            dt = datetime.fromtimestamp(call['timestamp'], self.timezone)
            duration = now - call['timestamp']
            
            table.add_row(
                dt.strftime(TIME_FORMAT),
                f"{duration}s",
                str(call['radio_id']),
                self.tg_description,
                "..."
            )
        
        # Add historical calls
        for call in self._recent_calls:
            dt = datetime.fromtimestamp(call['start_time'], self.timezone)
            duration = call.get('call_length', 0)
            
            # Get the first unit from srcList if available
            unit_id = str(call.get('srcList', [{}])[0].get('src', 'Unknown'))
            
            table.add_row(
                dt.strftime(TIME_FORMAT),
                f"{duration}s",
                unit_id,
                call.get('talkgroup_description', self.tg_description),
                call.get('transcription', '') or ''
            )
        
        return table

    def handle_update(self):
        """Handle database updates"""
        if self.interactive and self.live:
            try:
                self._fetch_data()
                self.live.update(self.create_table())
            except Exception as e:
                self.console.print(f"[red]Error updating display: {str(e)}")

    def run(self):
        """Main monitoring loop"""
        if self.interactive:
            self.console.clear()
            self.console.print(f"\n🎙️ Monitoring Talkgroup {self.talkgroup} - Press Ctrl+C to exit\n")
            
            self._fetch_data()
            initial_table = self.create_table()
            
            with Live(
                initial_table,
                refresh_per_second=4,
                vertical_overflow="crop",
                auto_refresh=True
            ) as live:
                self.live = live
                while self.running:
                    try:
                        time.sleep(0.25)
                    except (KeyboardInterrupt, SystemExit):
                        break
                    except Exception as e:
                        self.console.print(f"[red]Error in main loop: {str(e)}")
                        break
        else:
            self._fetch_data()
            self.console.print(self.create_table())
            while self.running:
                try:
                    signal.pause()
                except (KeyboardInterrupt, SystemExit):
                    break

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C signal"""
        self.running = False
        if self.live:
            self.live.stop()
        self.console.print("\n👋 Monitoring stopped")
        sys.exit(0)

def parse_args():
    parser = argparse.ArgumentParser(description='Talkgroup Monitor')
    parser.add_argument('talkgroup', type=int, help='Talkgroup number to monitor')
    parser.add_argument('--non-interactive', action='store_true', 
                      help='Run in non-interactive mode (append output instead of updating)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    monitor = TalkgroupMonitor(args.talkgroup, interactive=not args.non_interactive)
    monitor.run()
