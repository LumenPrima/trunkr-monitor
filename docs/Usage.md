# Usage Guide

## Starting the Monitor

1. Activate your virtual environment if you're using one:
```bash
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Run the application:
```bash
python main.py
```

## Interface Overview

The monitor displays two main panels:

### Left Panel - Active Calls
- Shows currently ongoing radio calls
- Updates in real-time
- Displays call details including duration

### Right Panel - Recent Calls
- Shows history of completed calls
- Maintains a log of recent activity
- Displays call details and duration

## Controls

- **Ctrl+C**: Gracefully exit the application
- The display automatically refreshes every 0.5 seconds

## Reading the Display

The monitor uses color coding and rich text formatting:
- Active calls are displayed with live duration counters
- Recent calls show completion times and total duration
- Error messages (if any) are displayed in red

## Troubleshooting

If you encounter issues:

1. Ensure all dependencies are installed
2. Check your terminal supports rich text formatting
3. Verify your terminal window is large enough for the display
4. Check the application logs for any error messages
