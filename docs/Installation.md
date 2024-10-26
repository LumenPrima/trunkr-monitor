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

### Database Setup

After installing MongoDB, set up the database and collections:

1. Connect to MongoDB:
```bash
mongosh
```

2. Create and use the database:
```javascript
use trunkr_database
```

3. Create collections with indexes:
```javascript
// Create collections
db.createCollection("calls_metadata")
db.createCollection("units_metadata")
db.createCollection("talkgroups_list")

// Create indexes for calls_metadata
db.calls_metadata.createIndex({ "hash": 1 }, { unique: true })
db.calls_metadata.createIndex({ "start_time": 1 })
db.calls_metadata.createIndex({ "talkgroup": 1 })

// Create indexes for units_metadata
db.units_metadata.createIndex({ "event_hash": 1, "timestamp": 1 })
```

### Getting Your MongoDB URI

The MongoDB URI is required for the application to connect to your database. The format depends on your setup:

#### Local Installation (No Authentication)
If you're running MongoDB locally without authentication:
```
mongodb://localhost:27017
```

#### Local Installation (With Authentication)
1. First, create a database user:
```javascript
use trunkr_database
db.createUser(
  {
    user: "trunkruser",
    pwd: "your_secure_password",
    roles: [
      { role: "readWrite", db: "trunkr_database" }
    ]
  }
)
```

2. Your URI will be:
```
mongodb://trunkruser:your_secure_password@localhost:27017/trunkr_database
```

#### Remote Installation
For a remote MongoDB server:
```
mongodb://username:password@server_ip:27017/trunkr_database
```

#### MongoDB Atlas
If using MongoDB Atlas:
1. Log in to your Atlas account
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the provided connection string
5. Replace `<password>` with your database user's password

### Testing the Connection

1. Test your connection string:
```bash
mongosh "your_connection_string"
```

2. Verify database access:
```javascript
use trunkr_database
db.calls_metadata.find().limit(1)
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

## Importing Talkgroups

The system requires a talkgroups list from trunk-recorder to map talkgroup IDs to their descriptions. The talkgroups file should be in CSV format with the following columns:
```
Decimal,Hex,Alpha Tag,Mode,Description,Tag,Category
```

Example format:
```csv
5000,1388,"FD01DISP","D","County Fire/EMS Dispatch","Fire Dispatch","Adams County (01)"
5001,1389,"FD01TAC04","D","County Fire Tac 4","Fire-Tac","Adams County (01)"
```

To import your talkgroups:

1. Make the import script executable:
```bash
chmod +x scripts/import_talkgroups.py
```

2. Run the import script with your talkgroups CSV file:
```bash
python scripts/import_talkgroups.py path/to/your/talkgroups.csv
```

The script will:
- Connect to MongoDB using your configured URI
- Create necessary indexes
- Remove any existing talkgroups
- Import the new talkgroups list

You can verify the import by checking the collection in MongoDB:
```javascript
use trunkr_database
db.talkgroups_list.find().limit(5)
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
