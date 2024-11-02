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
import sys
import curses
from rich.text import Text
from rich import print

class Pager:
    def __init__(self, talkgroup, description, total_convos):
        self.talkgroup = talkgroup
        self.description = description
        self.total_convos = total_convos
        self.current_pos = 1
        
    # Replace the format_status_line method with:
    def format_status_line(self):
        return (f"TG: {self.talkgroup} | {self.description} | "
                "Space/b:page Up/Down q:quit")
        
    def run(self, content_lines):
        try:
            # Initialize curses
            stdscr = curses.initscr()
            curses.start_color()
            curses.use_default_colors()
            curses.cbreak()
            curses.noecho()
            stdscr.keypad(1)
            
            # Get initial terminal size
            max_y, max_x = stdscr.getmaxyx()
            current_line = 0
            
            def display():
                stdscr.clear()
                # Display content area
                available_lines = max_y - 1  # Reserve last line for status
                for i in range(available_lines):
                    if current_line + i < len(content_lines):
                        try:
                            line = content_lines[current_line + i]
                            stdscr.addstr(i, 0, line[:max_x])
                        except curses.error:
                            pass
                
                # Display status line
                try:
                    status = self.format_status_line()
                    stdscr.addstr(max_y-1, 0, status[:max_x], curses.A_REVERSE)
                except curses.error:
                    pass
                
                stdscr.refresh()
            
            # Initial display
            display()
            
            # Main loop
            while True:
                c = stdscr.getch()
                if c == ord('q'):
                    break
                elif c == ord(' '):  # Page down
                    current_line = min(current_line + (max_y - 1), 
                                    max(0, len(content_lines) - (max_y - 1)))
                elif c == ord('b'):  # Page up
                    current_line = max(0, current_line - (max_y - 1))
                elif c == curses.KEY_DOWN:  # Line down
                    if current_line < len(content_lines) - (max_y - 1):
                        current_line += 1
                elif c == curses.KEY_UP:  # Line up
                    if current_line > 0:
                        current_line -= 1
                elif c == curses.KEY_RESIZE:
                    max_y, max_x = stdscr.getmaxyx()
                    
                # Update conversation position based on current line
                self.current_pos = (current_line // (max_y - 1)) + 1
                display()
                
        finally:
            curses.nocbreak()
            stdscr.keypad(0)
            curses.echo()
            curses.endwin()

def format_timestamp(timestamp):
    """Convert Unix timestamp to Eastern time"""
    tz = pytz.timezone('America/New_York')
    dt = datetime.fromtimestamp(timestamp, tz)
    return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

def print_conversation(calls):
    """Print a single conversation in plain text format"""
    lines = []
    for call in calls:
        timestamp = format_timestamp(call['start_time'])
        duration = f"{call.get('call_length', 0)}s"
        transcription = call.get('transcription', 'ENCRYPTED') or 'ENCRYPTED'
        
        # Format each line with fixed widths
        line = f"{timestamp}  {duration:>4}  {transcription}"
        lines.append(line)
    
    return lines

def main():
    parser = argparse.ArgumentParser(
        description='Display transcriptions for a specific talkgroup'
    )
    parser.add_argument('talkgroup', type=int)
    parser.add_argument('hours', type=float)
    parser.add_argument('--group-window', type=int, default=30)
    args = parser.parse_args()
    
    load_dotenv()
    
    try:
        # MongoDB setup
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
        db = client[os.getenv('DATABASE_NAME', 'trunkr_database')]
        
        # Get talkgroup info
        tg_info = db.talkgroups_list.find_one({"Decimal": args.talkgroup})
        description = tg_info.get('Description', '') if tg_info else ''
        
        # Get calls
        now = int(time.time())
        hours_ago = now - (int(args.hours * 3600))
        
        calls = list(db.calls_metadata.find({
            "talkgroup": args.talkgroup,
            "start_time": {"$gte": hours_ago}
        }).sort("start_time", 1))
        
        # Group calls
        grouped_calls = []
        if calls:
            current_group = [calls[0]]
            for call in calls[1:]:
                last_call = current_group[-1]
                if call['start_time'] <= (last_call['start_time'] + 
                                        last_call.get('call_length', 0) + 
                                        args.group_window):
                    current_group.append(call)
                else:
                    grouped_calls.append(current_group)
                    current_group = [call]
            grouped_calls.append(current_group)
        
        # Prepare display content
        content_lines = []
        content_lines.append(f"Talkgroup: {args.talkgroup}")
        content_lines.append(f"Description: {description}")
        content_lines.append(f"Time Range: Last {args.hours} hours")
        content_lines.append(f"Total Conversations: {len(grouped_calls)}")
        content_lines.append(f"Total Calls: {len(calls)}")
        content_lines.append("")
        
        for group in grouped_calls:
            start_time = format_timestamp(group[0]['start_time'])
            content_lines.append(f"=== Conversation at {start_time} ===")
            content_lines.extend(print_conversation(group))
            content_lines.append("")
            content_lines.append("")
        
        # Create and run pager
        pager = Pager(args.talkgroup, description, len(grouped_calls))
        pager.run(content_lines)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())