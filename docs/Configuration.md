# Configuration Guide

## Table Configuration

The `table_config.py` file contains settings for table display:
- Column definitions
- Display formats
- Styling preferences

### Customization Options

You can modify:
- Column widths
- Color schemes
- Update frequencies
- Display formats

## Database Configuration

Database settings can be adjusted in `database.py`:
- Data retention periods
- Query frequencies
- Storage options

## Display Configuration

The monitor's display can be customized through:

### Layout Options
- Panel sizes
- Update frequency
- Color schemes

### Data Display
- Number of recent calls shown
- Active call display format
- Time format preferences

## Performance Tuning

You can adjust:
- Refresh rate (default: 0.5 seconds)
- Data retention period
- Query optimization settings

## Environment Variables

The application checks for these optional environment variables:
- `REFRESH_RATE`: Display refresh frequency
- `MAX_RECENT_CALLS`: Maximum number of recent calls to display
- `LOG_LEVEL`: Logging verbosity
