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
- MongoDB (7.0 or higher recommended)
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

## MongoDB Installation

For detailed MongoDB 7.0 installation instructions, refer to the official documentation:
- [Install MongoDB Community Edition on Ubuntu](https://www.mongodb.com/docs/v7.0/tutorial/install-mongodb-on-ubuntu/)
- [Install MongoDB Community Edition on Windows](https://www.mongodb.com/docs/v7.0/tutorial/install-mongodb-on-windows/)
- [Install MongoDB Community Edition on macOS](https://www.mongodb.com/docs/v7.0/tutorial/install-mongodb-on-os-x/)

Quick setup for Ubuntu:

### Import MongoDB Public Key
```bash
sudo apt-get install gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor
```

### Add MongoDB Repository
For Ubuntu 22.04 (Jammy):
```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

### Install MongoDB
```bash
sudo apt-get update
sudo apt-get install -y mongodb-org
```

### Start MongoDB Service
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Verify Installation
```bash
mongosh
```

## Faster Whisper Server Setup

The project uses Faster Whisper for audio transcription. For detailed setup and configuration options, refer to:
- [Faster Whisper Server Documentation](https://github.com/SYSTRAN/faster-whisper)
- [Faster Whisper Server API Reference](https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/server.py)

Quick setup using Docker:

### GPU Support
```bash
docker run --gpus=all --publish 8000:8000 --volume ~/.cache/huggingface:/root/.cache/huggingface fedirz/faster-whisper-server:latest-cuda
```

### CPU Only
```bash
docker run --publish 8000:8000 --volume ~/.cache/huggingface:/root/.cache/huggingface fedirz/faster-whisper-server:latest-cpu
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

- [MongoDB Documentation](https://www.mongodb.com/docs/v7.0/)
- [Faster Whisper Documentation](https://github.com/SYSTRAN/faster-whisper)
- [Rich Documentation](https://github.com/Textualize/rich)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
