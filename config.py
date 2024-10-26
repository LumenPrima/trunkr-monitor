from datetime import datetime
import pytz

# MongoDB Configuration
MONGODB_URI = "mongodb://100.102.154.115:27017/?appName=MongoDB+Compass&directConnection=true"
DATABASE_NAME = "trunkr_database"
COLLECTION_NAME = "calls_metadata"

# Application Configuration
TIMEZONE = "America/New_York"
MAX_RECORDS = 10
TIME_FORMAT = "%H:%M:%S"
