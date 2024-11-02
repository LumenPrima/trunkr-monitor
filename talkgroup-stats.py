#!/usr/bin/env python3

from rich.console import Console
from rich.table import Table
from database import DatabaseManager
import argparse
from datetime import datetime, timedelta
import pytz
from config import TIMEZONE

class TalkgroupStats:
    def __init__(self):
        self.console = Console()
        self.db_manager = DatabaseManager()
        self.timezone = pytz.timezone(TIMEZONE)

    def get_talkgroup_stats(self, days=None):
        """
        Get statistics for all talkgroups with calls.
        
        Args:
            days: Optional number of days to limit the search
        """
        pipeline = []
        
        # Add date filter if specified
        if days:
            cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp())
            pipeline.append({
                "$match": {
                    "start_time": {"$gte": cutoff_time}
                }
            })
        
        # Aggregate calls by talkgroup
        pipeline.extend([
            {
                "$group": {
                    "_id": "$talkgroup",
                    "call_count": {"$sum": 1},
                    "total_duration": {"$sum": "$call_length"},
                    "first_seen": {"$min": "$start_time"},
                    "last_seen": {"$max": "$start_time"}
                }
            },
            # Join with talkgroups_list to get descriptions
            {
                "$lookup": {
                    "from": "talkgroups_list",
                    "localField": "_id",
                    "foreignField": "Decimal",
                    "as": "tg_info"
                }
            },
            {"$sort": {"call_count": -1}}
        ])

        return list(self.db_manager.db.calls_metadata.aggregate(pipeline))

    def display_stats(self, days=None):
        """Display talkgroup statistics in a formatted table"""
        table = Table(show_header=True, show_lines=True)
        
        table.add_column("TG", style="green", justify="right")
        table.add_column("Calls", style="cyan", justify="right")
        table.add_column("Total Duration", style="magenta", justify="right")
        table.add_column("Description", style="yellow")
        table.add_column("Last Activity", style="blue")

        stats = self.get_talkgroup_stats(days)
        
        for record in stats:
            # Get description from tg_info if available
            description = (record.get('tg_info', [{}])[0].get('Description', 'Unknown')
                         if record.get('tg_info') else 'Unknown')
            
            # Format duration in hours and minutes
            total_hours = record['total_duration'] / 3600
            formatted_duration = f"{total_hours:.1f}h"
            
            # Format last activity
            last_seen = datetime.fromtimestamp(record['last_seen'], self.timezone)
            last_seen_str = last_seen.strftime("%Y-%m-%d %H:%M")

            table.add_row(
                str(record['_id']),
                str(record['call_count']),
                formatted_duration,
                description,
                last_seen_str
            )

        # Add title showing time period
        if days:
            table.title = f"[bold blue]Talkgroup Activity (Last {days} days)"
        else:
            table.title = "[bold blue]Talkgroup Activity (All Time)"

        self.console.print(table)

def parse_args():
    parser = argparse.ArgumentParser(description='Display talkgroup usage statistics')
    parser.add_argument('--days', type=int, help='Number of days to analyze')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    stats = TalkgroupStats()
    stats.display_stats(args.days)
