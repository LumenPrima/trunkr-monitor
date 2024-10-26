# Configuration Guide

⚠️ **BETA PROJECT WARNING** ⚠️
This project is currently in BETA status and is NOT production-ready. Please note:
- Security features are incomplete and NOT suitable for production use
- Features are still under development and may change significantly
- Bugs and stability issues may exist
- No warranty or support is provided
- Use at your own risk

## Deployment Configurations

The system supports various deployment configurations to suit different needs:

### Local Development Setup
```bash
# MongoDB local
MONGODB_URI=mongodb://localhost:27017

# Whisper API local
WHISPER_API_URL=http://localhost:8000/v1/audio/transcriptions

# Debug enabled
DEBUG_MODE=True
```

### Distributed Setup
```bash
# MongoDB on dedicated server
MONGODB_URI=mongodb://mongodb-server:27017

# Whisper API on GPU server
WHISPER_API_URL=http://gpu-server:8000/v1/audio/transcriptions

# Production mode
DEBUG_MODE=False
```

### Cloud Setup
```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/

# Cloud Whisper API
WHISPER_API_URL=https://api.whisperservice.com/v1/audio/transcriptions

# Production mode
DEBUG_MODE=False
```

## Environment Configuration (.env)

The application uses environment variables for system-specific configuration. Create a `.env` file based on `.env.example`:

### Database Settings
```bash
# MongoDB connection settings
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=your_database

# Collection names
UNITS_COLLECTION=units_metadata
CALLS_COLLECTION=calls_metadata
TALKGROUPS_COLLECTION=talkgroups_list
```

### Application Settings
```bash
# Timezone configuration
TIMEZONE=America/New_York

# Debug mode
DEBUG_MODE=False
```

## MongoDB Operation Modes

The application supports two modes of operation based on your MongoDB setup:

### Change Streams Mode
- Requires MongoDB replica set
- Provides real-time updates
- Lower latency and resource usage
- Automatically enabled when replica set is detected

### Polling Mode
- Works with any MongoDB setup
- Polls for updates every second
- Higher latency but reliable
- Automatically used when change streams unavailable

## Configuration Loading (config.py)

The application loads configuration from environment variables with fallback defaults:

```python
# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'trunkr_database')

# Collection Names
UNITS_COLLECTION = os.getenv('UNITS_COLLECTION', 'units_metadata')
CALLS_COLLECTION = os.getenv('CALLS_COLLECTION', 'calls_metadata')
TALKGROUPS_COLLECTION = os.getenv('TALKGROUPS_COLLECTION', 'talkgroups_list')

# Application Configuration
TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')
DEBUG_MODE = bool(strtobool(os.getenv('DEBUG_MODE', 'False')))
```

## Table Configuration (table_config.py)

### Column Widths
```python
COLUMN_WIDTHS = {
    "active": {
        "time": 8,        # Duration/elapsed time
        "talkgroup": 6,   # Talkgroup ID
        "alpha_tag": 10,  # Talkgroup name (flexible)
        "unit": 10        # Radio unit ID
    },
    "recent": {
        "time": 10,       # Timestamp
        "talkgroup": 6,   # Talkgroup ID
        "description": 35  # Call description (flexible)
    },
    "units": {
        "time": 8,        # Timestamp
        "action": 9,      # Unit action
        "radio_id": 8,    # Radio identifier
        "tg_source": 7    # Source talkgroup
    }
}
```

### Color Schemes
```python
COLUMN_STYLES = {
    # Standard colors
    "time": "cyan",
    "talkgroup": "green",
    "alpha_tag": "yellow",
    "unit": "blue",
    "description": "yellow",
    "transcription": "white",
    
    # Structure colors
    "header": "bold magenta",
    "title": "bold blue",
    
    # Status colors
    "encrypted": "red",
    
    # Action-specific colors
    "action_colors": {
        "call": "green",        # Voice call
        "join": "cyan",         # Join call
        "on": "blue",          # Power on
        "off": "bright_black", # Power off
        "ans_req": "magenta",  # Answer request
        "location": "yellow",   # Location update
        "data": "white",       # Data transmission
        "ackresp": "dark_blue" # Acknowledgment
    }
}
```

## Best Practices

1. **MongoDB Configuration**
   - Use replica set in production for real-time updates
   - Configure authentication for security
   - Set appropriate read/write concerns
   - Monitor connection performance

2. **Environment Variables**
   - Never commit .env file to version control
   - Use .env.example as a template
   - Keep sensitive data in environment variables
   - Use secure values in production

3. **Time Configuration**
   - Use appropriate timezone for your location
   - Choose time format for your needs
   - Consider 24-hour format for clarity

4. **Performance Settings**
   - Use change streams when possible
   - Adjust polling interval if needed
   - Set appropriate cache sizes
   - Monitor resource usage

5. **Security** (Beta Limitations)
   - Current security features are incomplete
   - Authentication is not fully implemented
   - API endpoints lack proper security
   - Use in controlled environments only

## Development vs Production

### Development
```bash
# .env for development
MONGODB_URI=mongodb://localhost:27017
DEBUG_MODE=True
```

### Production
```bash
# .env for production
MONGODB_URI=mongodb://user:pass@host:port/db?replicaSet=rs0
DEBUG_MODE=False
```

## Troubleshooting

1. **MongoDB Connection**
   - Check connection string format
   - Verify network connectivity
   - Confirm authentication credentials
   - Check replica set status

2. **Update Mechanism**
   - Change streams require replica set
   - Polling works with any setup
   - Check logs for connection issues
   - Monitor update latency

3. **Performance Issues**
   - Monitor polling frequency
   - Check cache sizes
   - Verify connection pooling
   - Review resource usage

4. **Configuration Problems**
   - Validate environment variables
   - Check file permissions
   - Review log output
   - Test connection strings

## Known Limitations

1. **Security**
   - Limited authentication
   - Basic error handling
   - Minimal input validation
   - No encryption for local storage

2. **Features**
   - Some features incomplete
   - API endpoints in development
   - Limited error recovery
   - Basic monitoring capabilities

3. **Stability**
   - Potential memory leaks
   - Connection handling issues
   - Resource management concerns
   - Error handling gaps
