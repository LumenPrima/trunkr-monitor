# Table Column Width Configuration
# Defines the width of each column in characters for different table types.
# Values represent fixed widths, except where noted as "Allow to fill" which
# means the column can expand to use remaining space.
COLUMN_WIDTHS = {
    # Active calls table configuration
    "active": {
        "time": 8,        # Duration/elapsed time
        "talkgroup": 6,   # Talkgroup ID
        "alpha_tag": 10,  # Talkgroup name (flexible width)
        "unit": 10        # Radio unit ID
    },
    # Recent calls history table configuration
    "recent": {
        "time": 10,       # Timestamp
        "talkgroup": 6,   # Talkgroup ID
        "description": 35  # Call description (flexible width)
    },
    # Unit activity table configuration
    "units": {
        "time": 8,        # Timestamp
        "action": 9,      # Unit action (e.g., call, join, ans_req)
        "radio_id": 8,    # Radio identifier
        "tg_source": 7    # Source talkgroup
    }
}

# Table Style Configuration
# Defines the color scheme for different elements in the tables using Rich console colors.
# Colors are applied consistently across all tables for better visual organization.
COLUMN_STYLES = {
    # Standard column colors
    "time": "cyan",          # Timestamps and durations
    "talkgroup": "green",    # Talkgroup identifiers
    "alpha_tag": "yellow",   # Talkgroup names/descriptions
    "unit": "blue",          # Unit identifiers
    "description": "yellow", # Call descriptions
    "transcription": "white", # Voice transcriptions
    
    # Table structure colors
    "header": "bold magenta", # Column headers
    "title": "bold blue",     # Table titles
    
    # Special status colors
    "encrypted": "red",       # Encrypted transmissions
    
    # Unit activity colors
    "action": "magenta",      # Default action color
    "radio_id": "blue",       # Radio identifiers
    "short_name": "yellow",   # Short unit names
    
    # Specific action type colors for better visual distinction
    "action_colors": {
        "call": "green",        # Voice call initiation
        "join": "cyan",         # Unit joining a call
        "on": "blue",          # Unit power on/login
        "off": "bright_black", # Unit power off/logout
        "ans_req": "magenta",  # Answer request
        "location": "yellow",   # Location update
        "data": "white",       # Data transmission
        "ackresp": "dark_blue" # Acknowledgment response
    }
}
