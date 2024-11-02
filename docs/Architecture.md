# System Architecture

## Component Overview

### Core Components

1. **CallMonitor** (`monitor.py`)
   - Main application controller
   - Manages real-time display with Rich library
   - Handles interactive and non-interactive modes
   - Implements thread-safe data synchronization
   - Provides graceful shutdown handling
   - Manages display layout and refresh rates

2. **DatabaseManager** (`database.py`)
   - Implements dual update mechanism:
     - Primary: MongoDB change streams for real-time updates
     - Secondary: Fallback polling for reliability
   - Manages three data categories:
     - Active calls tracking
     - Recent call history
     - Unit activity monitoring
   - Provides automatic reconnection handling
   - Implements callback system for state updates
   - Handles data filtering and processing
   - Manages debug logging

3. **TableManager** (`tables.py`)
   - Creates and manages three display panels:
     - Active Calls table
     - Recent Calls table with transcriptions
     - Unit Activities table
   - Implements sophisticated filtering logic
   - Handles color-coded status display
   - Manages dynamic column sizing
   - Provides consistent timestamp formatting

### Supporting Components

4. **Configuration** (`config.py`)
   - Database connection settings
   - Timezone configuration
   - Debug mode settings
   - Time format preferences
   - Application-wide constants

5. **Table Configuration** (`table_config.py`)
   - Defines column widths and constraints
   - Specifies color schemes for different states
   - Configures action-specific styling
   - Manages table layout parameters

## Data Flow Architecture

```
[MongoDB Database]
      ↓
[Change Streams] ←→ [Fallback Polling]
      ↓                    ↓
   [DatabaseManager]
      ↓
   [Callbacks]
      ↓
  [CallMonitor]
      ↓
 [TableManager]
      ↓
[Rich Console Display]
```

## Update Mechanisms

### Primary: Change Streams
1. MongoDB change streams monitor collections in real-time
2. Separate streams for units and calls collections
3. Change events trigger immediate state updates
4. Callbacks notify display components
5. Tables refresh with new data

### Secondary: Fallback Polling
1. Activates when change streams are unavailable
2. Polls database at configurable intervals
3. Compares timestamps to prevent duplicates
4. Updates state only when changes detected
5. Seamlessly switches back to change streams when available

## Data Processing Pipeline

1. **Data Acquisition**
   - Change stream events or polling results
   - Timestamp-based filtering
   - Duplicate detection

2. **State Management**
   - Thread-safe data updates
   - Cache management
   - Active call tracking
   - History maintenance

3. **Display Processing**
   - Data filtering and sorting
   - Color coding application
   - Layout optimization
   - Dynamic width adjustment

## Technical Implementation

### Threading Model
- Main thread handles display
- Separate threads for:
  - Change stream monitoring
  - Fallback polling
  - Callback processing

### Error Handling
- Automatic reconnection for database issues
- Graceful degradation to polling
- Comprehensive error logging
- Recovery mechanisms

### Performance Optimizations
- Efficient data caching
- Smart polling intervals
- Optimized display refresh
- Memory usage management

### Security Considerations
- Encrypted transmission handling
- Safe database connections
- Proper error masking
- Secure shutdown procedures

## System Requirements

### Software Dependencies
- Python 3.x
- MongoDB with replica set
- Rich library for display
- PyMongo for database operations
- PyTZ for timezone handling

### Hardware Considerations
- Sufficient terminal height (24+ lines)
- Color-capable terminal
- Network connectivity
- Adequate CPU for real-time updates

## Extensibility

The system is designed for easy extension through:
- Modular component architecture
- Clear interface definitions
- Configurable styling system
- Pluggable callback mechanism
- Flexible data processing pipeline
