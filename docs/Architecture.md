# System Architecture

## Component Overview

### Core Components

1. **CallMonitor** (`monitor.py`)
   - Main application controller
   - Manages the real-time display
   - Handles signal interrupts
   - Coordinates between database and display components

2. **DatabaseManager** (`database.py`)
   - Manages data persistence
   - Handles active and recent call queries
   - Maintains call history

3. **TableManager** (`tables.py`)
   - Manages display formatting
   - Creates and updates Rich tables
   - Handles layout and styling

### Supporting Components

4. **Configuration** (`config.py`)
   - Stores application settings
   - Manages display preferences

5. **Table Configuration** (`table_config.py`)
   - Defines table structures
   - Sets column formats and styles

## Data Flow

```
[Call Data] → DatabaseManager → CallMonitor → TableManager → [Display]
                                     ↑
                              [Configuration]
```

## Update Cycle

1. Main loop runs every 0.5 seconds
2. Database queries for latest call data
3. Tables are regenerated with new data
4. Display is updated using Rich library

## Technical Details

- Built with Python's Rich library for terminal UI
- Uses signal handling for graceful shutdown
- Implements real-time monitoring with minimal resource usage
- Modular design for easy maintenance and extension
