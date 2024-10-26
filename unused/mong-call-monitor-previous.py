from pymongo import MongoClient
from datetime import datetime
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
import pytz

class CallMonitor:
    def __init__(self, connection_string="mongodb://100.102.154.115:27017/?appName=MongoDB+Compass&directConnection=true", db_name="trunkr_database"):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.console = Console()
        self.latest_timestamp = self.get_latest_timestamp()
        self.timezone = pytz.timezone('America/New_York')
        self.recent_calls = self.get_recent_calls()
        
    def get_latest_timestamp(self):
        """Get the most recent timestamp from the view"""
        latest_record = self.db.simplified_calls.find_one(
            sort=[("start_time", -1)]
        )
        return latest_record["start_time"] if latest_record else 0
    
    def get_recent_calls(self):
        """Get the 10 most recent calls"""
        return list(self.db.simplified_calls.find(
            sort=[("start_time", -1)]
        ).limit(10))[::-1]  # Reverse to show oldest first
    
    def format_timestamp(self, unix_timestamp):
        """Convert Unix timestamp to readable format"""
        dt = datetime.fromtimestamp(unix_timestamp, self.timezone)
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    def create_table(self, records):
        """Create a rich table with the records"""
        table = Table(show_header=True, header_style="bold magenta", title="Recent Transmissions")
        table.add_column("Time", style="cyan")
        table.add_column("Talkgroup", style="green")
        table.add_column("Description", style="yellow")
        table.add_column("Transcription", style="white", no_wrap=False)
        table.add_column("Audio File", style="blue")
        
        for record in records:
            table.add_row(
                self.format_timestamp(record["start_time"]),
                str(record["talkgroup"]),
                record["talkgroup_description"],
                record["transcription"],
                record["audio_file"]
            )
        return table
    
    def check_new_calls(self):
        """Check for new calls since last timestamp"""
        query = {"start_time": {"$gt": self.latest_timestamp}}
        new_records = list(self.db.simplified_calls.find(
            query,
            sort=[("start_time", 1)]
        ))
        
        if new_records:
            self.latest_timestamp = new_records[-1]["start_time"]
            # Update recent calls list
            self.recent_calls.extend(new_records)
            self.recent_calls = self.recent_calls[-10:]  # Keep only last 10
            return True
        return False
    
    def run(self):
        """Main monitoring loop"""
        self.console.clear()
        self.console.print(Panel.fit("🎙️ Radio Call Monitor - Press Ctrl+C to exit", 
                                   subtitle="Showing last 10 transmissions"))
        
        with Live(auto_refresh=False) as live:
            try:
                while True:
                    if self.check_new_calls() or not hasattr(self, 'last_update'):
                        table = self.create_table(self.recent_calls)
                        live.update(table, refresh=True)
                        self.last_update = time.time()
                    time.sleep(1)  # Check every second
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 Monitoring stopped")
                
if __name__ == "__main__":
    try:
        monitor = CallMonitor()
        monitor.run()
    except Exception as e:
        Console().print(f"[red]Error: {str(e)}")