# Trunkr Monitor

A real-time Python-based monitoring and visualization system for radio call data, featuring flexible MongoDB integration with support for both change streams and polling updates.

## Features

- Dual-mode database monitoring:
  - Real-time updates using MongoDB change streams (with replica set)
  - Automatic fallback to efficient polling (standard MongoDB)
- Three synchronized display panels:
  - 🔴 Active Calls: Currently ongoing radio transmissions
  - 📼 Recent Calls: Historical call records with transcriptions
  - 📟 Unit Activities: Individual radio unit actions and status updates
- Color-coded display for different types of activities and statuses
- Automatic handling of encrypted transmissions
- Configurable timezone and time format support
- Debug logging with configurable verbosity
- Interactive and non-interactive operation modes
- Graceful handling of connection issues and automatic reconnection
- Clean shutdown with Ctrl+C

## Project Structure

- `main.py` - Application entry point and argument parsing
- `monitor.py` - Core monitoring and display management
- `database.py` - Real-time database operations with change streams and fallback polling
- `tables.py` - Rich console table creation and formatting
- `table_config.py` - Table styling and layout configuration
- `config.py` - Configuration loading from environment variables
- `.env` - System-specific configuration (create from .env.example)
- `.env.example` - Template for environment configuration

## Documentation

Comprehensive documentation is available in the `docs` folder:

- [Installation Guide](docs/Installation.md) - Detailed setup instructions and requirements
- [Usage Guide](docs/Usage.md) - Operating instructions and command-line options
- [Architecture](docs/Architecture.md) - System design and component interactions
- [Configuration](docs/Configuration.md) - Available configuration options and customization

## Quick Start

1. Ensure Python 3.x is installed on your system
2. Clone this repository
3. Install required dependencies:
   ```bash
   pip install rich pymongo pytz python-dotenv
   ```
4. Set up environment configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```
5. Start monitoring:
   ```bash
   python main.py
   ```
   
   For non-interactive mode:
   ```bash
   python main.py --non-interactive
   ```

## MongoDB Setup Options

The application supports two modes of operation:

### Basic Setup
- Standard MongoDB installation
- No replica set required
- Uses efficient polling for updates
- Perfect for development and testing

### Advanced Setup
- MongoDB with replica set configuration
- Enables real-time change streams
- Lower latency and resource usage
- Recommended for production use

## Environment Configuration

Create a `.env` file based on `.env.example` with your settings:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=your_database

# Collection Names
UNITS_COLLECTION=units_metadata
CALLS_COLLECTION=calls_metadata
TALKGROUPS_COLLECTION=talkgroups_list

# Timezone Configuration
TIMEZONE=America/New_York

# Debug Mode
DEBUG_MODE=False
```

## System Requirements

- Python 3.x
- MongoDB (standard or replica set)
- Terminal with color support
- Sufficient terminal height for optimal display (minimum 24 lines recommended)

## Dependencies

- `rich`: Terminal formatting and tables
- `pymongo`: MongoDB database operations
- `pytz`: Timezone handling
- `python-dotenv`: Environment configuration management

## Logging

- Debug logs are written to `logs/trunkr.log`
- Log level is configurable via DEBUG_MODE in .env
- Logs include timestamps and relevant operational details

## Error Handling

- Automatic detection of MongoDB capabilities
- Seamless fallback between change streams and polling
- Graceful handling of connection issues
- Robust error logging and recovery mechanisms

## Performance

- Automatic selection of optimal update mechanism
- Efficient polling when change streams unavailable
- Optimized display refresh rates
- Memory-efficient data caching

## Security Notes

- Never commit .env file to version control
- Use secure MongoDB connection strings in production
- Protect sensitive configuration data
- Implement proper access controls

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
