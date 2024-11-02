#!/usr/bin/env python3

import argparse
from datetime import datetime
import time
import pytz
from pymongo import MongoClient
from rich.console import Console
from rich.table import Table
import os
from dotenv import load_dotenv

def parse_args():
    parser = argparse.ArgumentParser(
        description='Display transcriptions for a specific talkgroup from the last N hours'
    )
    parser.add_argument('talkgroup', type=int, help='Talkgroup number to query')
    parser.add_argument('hours', type=float, help='Hours ago to search (can be decimal)')
    parser.add_argument('--uri', help='MongoDB URI (optional, defaults to env var)')
    parser.add_argument('--db', help='Database name (optional, defaults to env var)')
    return parser.parse_args()

def format_timestamp(timestamp):
    """Convert Unix timestamp to Eastern time"""
    tz = pytz.timezone('America/New_York')
    dt = datetime.fromtimestamp(timestamp, tz)
    return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

def get_transcriptions(client, db_name, talkgroup, hours):
    """Query MongoDB for transcriptions"""
    db = client[db_name]
    
    # Calculate timestamp for N hours ago
    now = int(time.time())
    hours_ago = now - (int(hours * 3600))
    
    # Get talkgroup info for description
    tg_info = db.talkgroups_list.find_one({"Decimal": talkgroup})
    tg_description = tg_info.get('Description', '') if tg_info else ''
    
    # Query for calls
    calls = db.calls_metadata.find({
        "talkgroup": talkgroup,
        "start_time": {"$gte": hours_ago}
    }).sort("start_time", -1)
    
    return calls, tg_description

def main():
    # Parse arguments
    args = parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Setup MongoDB connection
    mongo_uri = args.uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = args.db or os.getenv('DATABASE_NAME', 'trunkr_database')
    
    # Setup Rich console
    console = Console()
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        
        # Get transcriptions
        calls, tg_description = get_transcriptions(
            client, db_name, args.talkgroup, args.hours
        )
        
        # Create table
        table = Table(show_header=True, show_lines=True)
        table.add_column("Time", style="cyan", width=25)
        table.add_column("Duration", style="magenta", justify="right", width=8)
        table.add_column("Transcription", style="white")
        
        # Add header showing query info
        console.print(f"\n[yellow]Talkgroup:[/yellow] {args.talkgroup}")
        console.print(f"[yellow]Description:[/yellow] {tg_description}")
        console.print(f"[yellow]Time Range:[/yellow] Last {args.hours} hours\n")
        
        # Add rows
        count = 0
        for call in calls:
            time_str = format_timestamp(call['start_time'])
            duration = f"{call.get('call_length', 0)}s"
            transcription = call.get('transcription', 'ENCRYPTED') or 'ENCRYPTED'
            
            # Style encrypted calls differently
            if transcription == 'ENCRYPTED':
                style = "red"
            else:
                style = None
                
            table.add_row(time_str, duration, transcription, style=style)
            count += 1
        
        # Show results
        console.print(table)
        console.print(f"\n[green]Found {count} calls[/green]\n")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())
