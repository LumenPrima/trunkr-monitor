from rich.table import Table
from datetime import datetime
import time
from table_config import COLUMN_WIDTHS, COLUMN_STYLES
from config import TIMEZONE, TIME_FORMAT
import pytz

class TableManager:
    """
    Manages the creation and formatting of Rich console tables for displaying
    radio system monitoring data. Handles three main table types:
    - Active Calls: Currently ongoing radio transmissions
    - Recent Calls: Historical call records with transcriptions
    - Unit Activities: Individual radio unit actions and status updates
    """
    def __init__(self):
        # Initialize timezone for consistent timestamp formatting
        self.timezone = pytz.timezone(TIMEZONE)

    def create_active_calls_table(self, records, recent_records):
        """
        Creates a table displaying currently active radio calls.
        
        Filters out completed calls by comparing start times against recent call
        end times for the same talkgroup to prevent duplicate display of calls
        that have already ended.

        Args:
            records: List of active call records from DatabaseManager
            recent_records: List of recent call records for filtering

        Returns:
            Rich Table object configured for active calls display
        """
        table = Table(
            title="🔴 Active Calls",
            title_style=COLUMN_STYLES["title"],
            pad_edge=False,
            padding=(0, 1),
            collapse_padding=True,
            expand=False  # Don't expand to full width
        )
        
        # Configure columns with specific widths and styles
        table.add_column("Time", 
            style=COLUMN_STYLES["time"], 
            width=COLUMN_WIDTHS["active"]["time"]
        )
        table.add_column("TG", 
            style=COLUMN_STYLES["talkgroup"], 
            width=COLUMN_WIDTHS["active"]["talkgroup"]
        )
        table.add_column("Alpha Tag", 
            style=COLUMN_STYLES["alpha_tag"],
        )
        table.add_column("Unit", 
            style=COLUMN_STYLES["unit"], 
            width=COLUMN_WIDTHS["active"]["unit"]
        )
        
        # Filter out calls that have ended based on recent call records
        # A call is considered active only if its start time is after all
        # end times for the same talkgroup in recent calls
        filtered_records = []
        for record in records:
            tg = record["talkgroup"]
            start_time = record["start_time"]
            
            # Get all end times for this talkgroup from recent calls
            tg_recent_end_times = [
                r.get("end_time", 0) 
                for r in recent_records 
                if r["talkgroup"] == tg
            ]
            
            # Include only if start time is after ALL end times
            if not tg_recent_end_times or start_time > max(tg_recent_end_times):
                filtered_records.append(record)
        
        # Display up to 15 most recent active calls
        for record in filtered_records[:15]:
            dt = datetime.fromtimestamp(record["start_time"], self.timezone)
            table.add_row(
                dt.strftime(TIME_FORMAT),
                str(record["talkgroup"]),
                record.get("alpha_tag", ""),
                str(record["initiating_unit"])
            )
        return table
        
    def create_recent_calls_table(self, records):
        """
        Creates a table displaying recent call history with transcriptions.
        
        Includes special formatting for encrypted calls and supports variable
        width transcription display. Calls are sorted by start time with
        newest first.

        Args:
            records: List of recent call records from DatabaseManager

        Returns:
            Rich Table object configured for recent calls display
        """
        table = Table(
            title="📼 Recent Calls",
            title_style=COLUMN_STYLES["title"],
            pad_edge=False,
            padding=(0, 1),
            collapse_padding=True,
            expand=True,      # Expand to use available width
            show_lines=True   # Visual separation between rows
        )
        
        # Configure columns with specific widths and styles
        table.add_column("Time", 
            style=COLUMN_STYLES["time"], 
            width=COLUMN_WIDTHS["recent"]["time"],
            no_wrap=True
        )
        table.add_column("TG", 
            style=COLUMN_STYLES["talkgroup"], 
            width=COLUMN_WIDTHS["recent"]["talkgroup"],
            no_wrap=True
        )
        table.add_column("Description", 
            style=COLUMN_STYLES["description"], 
            width=COLUMN_WIDTHS["recent"]["description"]
        )
        # Transcription column expands to fill remaining space
        table.add_column("Transcription", 
            style=COLUMN_STYLES["transcription"]
        )
        
        # Sort by start_time descending (newest first)
        sorted_records = sorted(records, key=lambda x: x["start_time"], reverse=True)
        
        # Display all available records
        for record in sorted_records:
            # Use encrypted style for calls without transcription
            time_style = COLUMN_STYLES["encrypted"] if not record.get("transcription") else COLUMN_STYLES["time"]
            dt = datetime.fromtimestamp(record["start_time"], self.timezone)
            table.add_row(
                dt.strftime(TIME_FORMAT),
                str(record["talkgroup"]),
                record.get("talkgroup_description", ""),
                record.get("transcription", "ENCRYPTED") or "ENCRYPTED",
                style=time_style if time_style == COLUMN_STYLES["encrypted"] else None
            )
        return table
    
    def create_units_table(self, records):
        """
        Creates a table displaying individual unit activities and status updates.
        
        Supports color-coded actions based on activity type and displays
        both talkgroup and source information. Activities are sorted by
        timestamp with newest first.

        Args:
            records: List of unit activity records from DatabaseManager

        Returns:
            Rich Table object configured for unit activities display
        """
        table = Table(
            title="📟 Unit Activities",
            title_style=COLUMN_STYLES["title"],
            pad_edge=False,
            padding=(0, 0),
            collapse_padding=True,
            expand=True  # Expand to use available width
        )
        
        # Configure columns with specific widths and styles
        table.add_column("Time", 
            style=COLUMN_STYLES["time"], 
            width=COLUMN_WIDTHS["units"]["time"]
        )
        table.add_column("Action", 
            width=COLUMN_WIDTHS["units"]["action"]
        )
        table.add_column("Radio ID", 
            style=COLUMN_STYLES["radio_id"], 
            width=COLUMN_WIDTHS["units"]["radio_id"]
        )
        table.add_column("TG/Src", 
            style=COLUMN_STYLES["talkgroup"], 
            width=COLUMN_WIDTHS["units"]["tg_source"]
        )
        
        # Sort by timestamp descending (newest first)
        sorted_records = sorted(records, key=lambda x: x["timestamp"], reverse=True)
        
        # Display all available records with color-coded actions
        for record in sorted_records:
            dt = datetime.fromtimestamp(record["timestamp"], self.timezone)
            # Use talkgroup if available, otherwise use source
            tg_source = record.get("talkgroup", record.get("source", ""))
            # Get action-specific color, default to white if action type unknown
            action_color = COLUMN_STYLES["action_colors"].get(record["action"], "white")
            
            table.add_row(
                dt.strftime(TIME_FORMAT),
                record["action"],
                str(record["radio_id"]),
                str(tg_source),
                style=action_color
            )
        return table
