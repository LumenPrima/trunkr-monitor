from pymongo import MongoClient
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
import pytz
import threading
import queue
import signal
import sys
import time

# Configuration Variables
MONGODB_URI = "mongodb://100.102.154.115:27017/?appName=MongoDB+Compass&directConnection=true"
DATABASE_NAME = "trunkr_database"
COLLECTION_NAME = "calls_metadata"
TIMEZONE = "America/New_York"
MAX_RECORDS = 10

# Table Display Configuration
COLUMN_WIDTHS = {
    "active": {
        "time": 8,
        "talkgroup": 8,
        "alpha_tag": 20,
        "unit": 10
    },
    "recent": {
        "time": 10,
        "talkgroup": 8,
        "description": 30,
        "transcription": 30
    }
}

COLUMN_STYLES = {
    "time": "cyan",
    "talkgroup": "green",
    "alpha_tag": "yellow",
    "unit": "blue",
    "description": "yellow", 
    "transcription": "white",
    "header": "bold magenta",
    "title": "bold blue",
    "encrypted": "red"
}

TIME_FORMAT = "%H:%M:%S"

class CallMonitor:
    def __init__(self):
        self.connection_uri = MONGODB_URI
        self.client = MongoClient(self.connection_uri)
        self.db = self.client[DATABASE_NAME]
        self.console = Console()
        self.timezone = pytz.timezone(TIMEZONE)
        self.running = True
        self.live = None
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def create_active_calls_table(self, records):
        """Create table for active calls"""
        table = Table(
            title="🔴 Active Calls",
            title_style="bold red",
            box=None,
            pad_edge=False,
            width=60
        )
        
        table.add_column("Time", style="cyan", width=8)
        table.add_column("TG", style="green", width=8)
        table.add_column("Alpha Tag", style="yellow", width=20)
        table.add_column("Unit", style="blue", width=10)
        
        now = int(time.time())
        for record in records:
            elapsed = now - record["start_time"]
            table.add_row(
                f"{elapsed//60}:{elapsed%60:02d}",
                str(record["talkgroup"]),
                record.get("alpha_tag", ""),
                str(record["initiating_unit"])
            )
        return table
        
    def create_recent_calls_table(self, records):
        """Create table for completed calls"""
        table = Table(
            title="📼 Recent Calls",
            title_style="bold blue",
            box=None,
            pad_edge=False,
            width=80
        )
        
        table.add_column("Time", style="cyan", width=10)
        table.add_column("TG", style="green", width=8)
        table.add_column("Description", style="yellow", width=30)
        table.add_column("Transcription", style="white", width=30)
        
        for record in records:
            # Check if encrypted (no transcription)
            time_style = "red" if not record.get("transcription") else "cyan"
            dt = datetime.fromtimestamp(record["start_time"], self.timezone)
            table.add_row(
                dt.strftime("%H:%M:%S"),
                str(record["talkgroup"]),
                record.get("talkgroup_description", "")[:30],
                (record.get("transcription", "ENCRYPTED") or "ENCRYPTED")[:30],
                style=time_style if time_style == "red" else None
            )
        return table

    def create_layout(self):
        """Create side-by-side layout"""
        layout = Layout()
        layout.split_row(
            Layout(name="active"),
            Layout(name="recent")
        )
        return layout
    
    def get_active_calls(self):
        """Get active calls from units_metadata"""
        now = int(time.time())
        pipeline = [
            {
                "$match": {
                    "action": "call",
                    "timestamp": {"$gte": now - 180}  # Last 3 minutes
                }
            },
            {
                "$group": {
                    "_id": "$talkgroup",
                    "start_time": {"$min": "$timestamp"},  # Get earliest timestamp for talkgroup
                    "initiating_unit": {"$first": "$radio_id"},
                    "latest_time": {"$max": "$timestamp"}  # Add this to sort by most recent activity
                }
            },
            {
                "$lookup": {
                    "from": "talkgroups_list",
                    "let": {"tg": {"$toInt": "$_id"}},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {"$eq": ["$Decimal", "$$tg"]}
                            }
                        }
                    ],
                    "as": "talkgroup_info"
                }
            },
            {
                "$project": {
                    "talkgroup": "$_id",
                    "start_time": 1,
                    "initiating_unit": 1,
                    "latest_time": 1,
                    "alpha_tag": {"$arrayElemAt": ["$talkgroup_info.Alpha Tag", 0]}
                }
            },
            {
                "$sort": {
                    "latest_time": -1,  # Sort by most recent activity first
                    "talkgroup": 1      # Then by talkgroup number for stable ordering
                }
            }
        ]
        return list(self.db.units_metadata.aggregate(pipeline))

    def get_recent_calls(self):
        """Get recent completed calls"""
        now = int(time.time())
        return list(self.db.calls_metadata.find(
            {"start_time": {"$gte": now - 300}},
            sort=[("start_time", 1)],  # Changed from -1 to 1 to sort oldest to newest
            limit=MAX_RECORDS
        ))

    def update_display(self):
        """Update both tables"""
        active_calls = self.get_active_calls()
        recent_calls = self.get_recent_calls()
        
        layout = self.create_layout()
        layout["active"].update(self.create_active_calls_table(active_calls))
        layout["recent"].update(self.create_recent_calls_table(recent_calls))
        
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
