from rich.table import Table
from datetime import datetime
import time
from table_config import COLUMN_WIDTHS, COLUMN_STYLES
from config import TIMEZONE, TIME_FORMAT
import pytz

class TableManager:
    def __init__(self):
        self.timezone = pytz.timezone(TIMEZONE)

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
        
        for record in records:
            dt = datetime.fromtimestamp(record["start_time"], self.timezone)
            table.add_row(
                dt.strftime(TIME_FORMAT),
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
            time_style = "red" if not record.get("transcription") else "cyan"
            dt = datetime.fromtimestamp(record["start_time"], self.timezone)
            table.add_row(
                dt.strftime(TIME_FORMAT),
                str(record["talkgroup"]),
                record.get("talkgroup_description", "")[:30],
                (record.get("transcription", "ENCRYPTED") or "ENCRYPTED")[:30],
                style=time_style if time_style == "red" else None
            )
        return table
