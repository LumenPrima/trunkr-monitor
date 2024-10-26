# Installation Guide

⚠️ **BETA PROJECT WARNING** ⚠️
This project is currently in BETA status and is NOT production-ready. Please note:
- Security features are incomplete and NOT suitable for production use
- Features are still under development and may change significantly
- Bugs and stability issues may exist
- No warranty or support is provided
- Use at your own risk

## System Requirements

### Software Prerequisites
- Python 3.x (3.7 or higher recommended)
- MongoDB (replica set optional)
- Git (for version control)
- Terminal with color support

### Hardware Requirements
- Minimum terminal height: 24 lines recommended
- Network connectivity for MongoDB access
- Sufficient CPU for real-time updates

## Deployment Options

The system can be deployed in several configurations:

### 1. All-Local Setup
- MongoDB running locally
- Faster Whisper Server running locally
- Monitor application running locally
- Best for development and testing

### 2. Distributed Setup
- MongoDB on a dedicated server
- Faster Whisper Server on a separate machine (especially for GPU support)
- Monitor application on user workstations
- Better for team environments

### 3. Cloud Setup
- MongoDB Atlas for database
- Cloud-hosted Whisper API
- Monitor application running locally
- Suitable for scalable deployments

Choose the setup that best matches your needs and resources.

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/LumenPrima/trunkr-monitor.git
cd trunkr-monitor
```

2. Create and activate a virtual environment (recommended):
```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install rich pymongo pytz python-dotenv
```

## Environment Configuration

1. Create environment file:
```bash
# Copy the example environment file
cp .env.example .env
```

2. Configure your environment variables:
```bash
# Edit .env file with your settings
# MongoDB Configuration
MONGODB_URI=mongodb://your-mongodb-uri
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

## MongoDB Setup

The application supports two modes of operation:

### Basic Setup (Polling Mode)
- Standard MongoDB installation
- No replica set required
- Uses polling for updates (every 1 second)
- Suitable for development and testing

### Advanced Setup (Change Streams Mode)
- MongoDB replica set configuration
- Real-time updates via change streams
- Better performance and lower latency
- Recommended for production use

To configure a replica set (optional):
1. Stop MongoDB
2. Add replica set configuration to mongod.conf:
```yaml
replication:
  replSetName: "rs0"
```
3. Start MongoDB
4. Initialize the replica set:
```bash
mongosh
> rs.initiate()
```

## Configuration Verification

1. MongoDB Settings:
   - Verify MongoDB connection string in .env
   - Ensure database name is correct
   - Verify collection names match your setup
   - Application will automatically detect if change streams are available

2. Timezone Configuration:
   - Set appropriate timezone for your location
   - Valid timezone names from the IANA Time Zone Database

3. Debug Settings:
   - Set DEBUG_MODE=True for development
   - Set DEBUG_MODE=False for production

## Verification

1. Start the application:
```bash
# Interactive mode (default)
python main.py

# Non-interactive mode
python main.py --non-interactive
```

2. Verify the display components:
   - 🔴 Active Calls panel (top left)
   - 📟 Unit Activities panel (bottom left)
   - 📼 Recent Calls panel (right)

3. Check the logs:
```bash
tail -f logs/trunkr.log
```

## Dependencies Explained

### Core Dependencies
- `rich`: Terminal UI framework
  - Provides table formatting
  - Handles color coding
  - Manages layout

- `pymongo`: MongoDB interface
  - Manages database connections
  - Implements change streams (when available)
  - Handles queries and updates

- `pytz`: Timezone support
  - Handles timestamp conversions
  - Provides consistent time display
  - Manages timezone-aware operations

- `python-dotenv`: Environment configuration
  - Loads environment variables
  - Manages configuration
  - Secures sensitive data

## Troubleshooting

### Common Issues

1. MongoDB Connection:
```
Problem: Cannot connect to MongoDB
Solution: Verify MongoDB is running and connection string is correct

Problem: Change streams not working
Solution: Normal if not using replica set, application will use polling instead
```

2. Environment Variables:
```
Problem: Environment variables not loading
Solution: Verify .env file exists and has correct permissions
```

3. Display Issues:
```
Problem: Truncated or misaligned display
Solution: Ensure terminal window is at least 24 lines high
```

4. Color Support:
```
Problem: Missing or incorrect colors
Solution: Use a terminal that supports ANSI color codes
```

### Debug Mode

Enable debug mode in .env for detailed logging:
```
DEBUG_MODE=True
```

This will provide verbose output in `logs/trunkr.log`

## Updating

To update an existing installation:

1. Pull latest changes:
```bash
git pull origin main
```

2. Update dependencies:
```bash
pip install -r requirements.txt  # if requirements.txt exists
```

3. Check configuration:
```bash
# Review any new environment variables in .env.example
# Update your .env file accordingly
```

## Security Notes

⚠️ **IMPORTANT SECURITY NOTICE** ⚠️
This is a beta project with incomplete security features. Current limitations include:
- No built-in authentication system
- Limited input validation
- Basic error handling
- No encryption for local storage
- Minimal security hardening

For any use beyond testing and development:
1. Implement proper authentication
2. Add input validation
3. Secure all API endpoints
4. Encrypt sensitive data
5. Follow security best practices

## Additional Resources

- MongoDB Documentation: [Change Streams](https://docs.mongodb.com/manual/changeStreams/)
- Rich Documentation: [Rich GitHub](https://github.com/Textualize/rich)
- PyMongo Documentation: [PyMongo](https://pymongo.readthedocs.io/)
- Python-dotenv Documentation: [python-dotenv](https://github.com/theskumar/python-dotenv)
