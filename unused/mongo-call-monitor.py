# Configuration Variables
MONGODB_URI = "mongodb://100.102.154.115:27017/?appName=MongoDB+Compass&directConnection=true"
DATABASE_NAME = "trunkr_database"
COLLECTION_NAME = "calls_metadata"
TIMEZONE = "America/New_York"
MAX_RECORDS = 10

# Table Display Configuration
COLUMN_WIDTHS = {
    "time": 30,
    "talkgroup": 12,
    "description": 40,
    "transcription": 50,
    "audio": 40
}

COLUMN_STYLES = {
    "time": "cyan",
    "talkgroup": "green",
    "description": "yellow",
    "transcription": "white",
    "audio": "blue",
    "header": "bold magenta",
    "title": "bold blue"
}

FIELDS_TO_FETCH = {
    "start_time": 1,
    "talkgroup": 1,
    "talkgroup_description": 1,
    "transcription": 1,
    "audio_file": 1,
    "_id": 1
}

TIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

from pymongo import MongoClient
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
import pytz
import threading
import queue
import signal
import sys

class CallMonitor:
    def __init__(self):
        self.connection_uri = MONGODB_URI
        self.client = MongoClient(self.connection_uri)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[COLLECTION_NAME]
        self.console = Console()
        self.timezone = pytz.timezone(TIMEZONE)
        self.updates_queue = queue.Queue()
        self.running = True
        self.live = None
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        self.running = False
        if self.live:
            self.live.stop()
        self.console.print("\n👋 Monitoring stopped")
        sys.exit(0)
        
    def get_recent_calls(self):
        """Get the most recent calls"""
        try:
            cursor = self.collection.find(
                projection=FIELDS_TO_FETCH,
                sort=[("start_time", -1)]
            ).limit(MAX_RECORDS)
            
            calls = list(cursor)
            self.console.print(f"[green]Found {len(calls)} recent calls")
            return calls[::-1]  # Reverse to show oldest first
        except Exception as e:
            self.console.print(f"[red]Error fetching recent calls: {str(e)}")
            return []
    
    def format_timestamp(self, unix_timestamp):
        """Convert Unix timestamp to readable format"""
        dt = datetime.fromtimestamp(unix_timestamp, self.timezone)
        return dt.strftime(TIME_FORMAT)
    
    def create_table(self, records):
        """Create a rich table with the records"""
        table = Table(
            show_header=True, 
            header_style=COLUMN_STYLES["header"],
            title="Live Radio Transmissions Monitor",
            title_style=COLUMN_STYLES["title"]
        )
        
        # Add columns using configuration
        table.add_column("Time", style=COLUMN_STYLES["time"], width=COLUMN_WIDTHS["time"])
        table.add_column("Talkgroup", style=COLUMN_STYLES["talkgroup"], width=COLUMN_WIDTHS["talkgroup"])
        table.add_column("Description", style=COLUMN_STYLES["description"], width=COLUMN_WIDTHS["description"])
        table.add_column("Transcription", style=COLUMN_STYLES["transcription"], width=COLUMN_WIDTHS["transcription"], no_wrap=False)
        table.add_column("Audio File", style=COLUMN_STYLES["audio"], width=COLUMN_WIDTHS["audio"])
        
        for record in records:
            try:
                table.add_row(
                    self.format_timestamp(record["start_time"]),
                    str(record["talkgroup"]),
                    record.get("talkgroup_description", ""),
                    record.get("transcription", ""),
                    record.get("audio_file", "")
                )
            except Exception as e:
                self.console.print(f"[red]Error adding row: {str(e)}")
        return table

    def watch_collection(self):
        """Monitor the collection for changes"""
        try:
            # Set up change stream with a resume token
            change_stream = self.collection.watch(
                [{'$match': {'operationType': 'insert'}}],
                full_document='updateLookup',
                max_await_time_ms=1000  # 1 second timeout
            )
            
            self.console.print("[green]Successfully connected to change stream")
            
            while self.running:
                try:
                    change = change_stream.next()
                    if change and change['operationType'] == 'insert':
                        new_document = change['fullDocument']
                        self.recent_calls.append(new_document)
                        self.recent_calls = self.recent_calls[-MAX_RECORDS:]
                        if self.live:
                            table = self.create_table(self.recent_calls)
                            self.live.update(table, refresh=True)
                except StopIteration:
                    continue
                    
        except Exception as e:
            self.console.print(f"[red]Change stream error: {str(e)}")
            
    def run(self):
        """Main monitoring loop"""
        self.console.clear()
        self.console.print(Panel.fit(
            "🎙️ Real-time Radio Call Monitor - Press Ctrl+C to exit",
            subtitle="Connected to MongoDB"
        ))
        
        # Get initial data
        self.recent_calls = self.get_recent_calls()
        
        # Create initial table
        table = self.create_table(self.recent_calls)
        
        # Start the change stream monitoring in a separate thread
        watch_thread = threading.Thread(target=self.watch_collection, daemon=True)
        watch_thread.start()
        
        with Live(table, auto_refresh=False, transient=False) as live:
            self.live = live
            # Keep the main thread alive
            while self.running:
                try:
                    threading.Event().wait(0.1)
                except Exception as e:
                    self.console.print(f"[red]Error in main loop: {str(e)}")
                    break

if __name__ == "__main__":
    monitor = CallMonitor()
    monitor.run()