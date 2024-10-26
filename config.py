from datetime import datetime
import pytz
from dotenv import load_dotenv
import os
from distutils.util import strtobool

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'trunkr_database')

# Collection Names
UNITS_COLLECTION = os.getenv('UNITS_COLLECTION', 'units_metadata')
CALLS_COLLECTION = os.getenv('CALLS_COLLECTION', 'calls_metadata')
TALKGROUPS_COLLECTION = os.getenv('TALKGROUPS_COLLECTION', 'talkgroups_list')

# Application Configuration
TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')
TIME_FORMAT = "%H:%M:%S"

# Debug Configuration
DEBUG_MODE = bool(strtobool(os.getenv('DEBUG_MODE', 'False')))

# Validate timezone
try:
    pytz.timezone(TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    print(f"Warning: Invalid timezone {TIMEZONE}, falling back to America/New_York")
    TIMEZONE = "America/New_York"
