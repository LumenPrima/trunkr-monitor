# Usage Guide

## Running the Monitor

1. Activate your virtual environment (if using):
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

2. Start the application:
```bash
# Interactive mode (default)
python main.py

# Non-interactive mode
python main.py --non-interactive
```

## Display Layout

The monitor features three synchronized display panels:

### 🔴 Active Calls (Top Left)
- Currently ongoing radio transmissions
- Real-time updates via change streams
- Shows:
  - Time: Call duration in HH:MM:SS
  - TG: Talkgroup number
  - Alpha Tag: Talkgroup description
  - Unit: Initiating radio unit

### 📟 Unit Activities (Bottom Left)
- Individual radio unit actions
- Color-coded by activity type:
  - `call`: Green - Voice call initiation
  - `join`: Cyan - Unit joining a call
  - `on`: Blue - Unit power on/login
  - `off`: Dark gray - Unit power off/logout
  - `ans_req`: Magenta - Answer request
  - `location`: Yellow - Location update
  - `data`: White - Data transmission
  - `ackresp`: Dark blue - Acknowledgment response

### 📼 Recent Calls (Right)
- Historical call records
- Shows:
  - Time: Call timestamp
  - TG: Talkgroup number
  - Description: Call details
  - Transcription: Voice transcription (if available)
- Red highlighting for encrypted transmissions

## Operation Modes

### Interactive Mode (Default)
- Live updating display
- Real-time visual feedback
- Automatic screen refresh
- Recommended for active monitoring

### Non-Interactive Mode
- Append-only output
- Suitable for logging
- Can be redirected to files
- Useful for automated monitoring

## Controls and Navigation

- **Ctrl+C**: Clean application shutdown
- Display automatically updates with new data
- No manual refresh needed
- Terminal scrolling for history review

## Color Coding Guide

### Status Colors
- Green: Active transmissions
- Cyan: Timestamps
- Yellow: Descriptions and tags
- Blue: Unit identifiers
- Red: Encrypted transmissions
- Magenta: Headers and special actions

### Activity Colors
- Each unit action has a distinct color
- Helps quickly identify activity types
- Consistent across all displays
- Configurable in table_config.py

## Data Interpretation

### Active Calls
- Most recent calls at the top
- Duration shown in elapsed time
- Talkgroup tags for quick identification
- Unit IDs of initiating radios

### Unit Activities
- Chronological activity log
- Color-coded actions
- Source/destination tracking
- Timestamp for each event

### Recent Calls
- Complete call history
- Transcription status
- Call descriptions
- Temporal context

## Monitoring Tips

1. **Real-Time Monitoring**
   - Watch Active Calls for current activity
   - Monitor Unit Activities for detailed events
   - Check Recent Calls for context

2. **Pattern Recognition**
   - Use color coding to identify activity types
   - Track unit movements across talkgroups
   - Monitor encrypted transmission patterns

3. **Troubleshooting**
   - Check connection status in logs
   - Monitor for error messages
   - Verify data freshness

## Performance Optimization

1. **Terminal Size**
   - Minimum 24 lines recommended
   - Width affects description display
   - Adjust terminal for optimal viewing

2. **Update Frequency**
   - Real-time updates via change streams
   - Fallback polling if needed
   - Automatic performance adjustment

3. **Resource Usage**
   - Efficient memory management
   - Optimized display updates
   - Background thread management

## Troubleshooting

### Common Issues

1. **Display Problems**
```
Issue: Truncated or misaligned display
Fix: Increase terminal size
```

2. **Update Delays**
```
Issue: Slow updates
Fix: Check MongoDB connection and network
```

3. **Color Issues**
```
Issue: Missing or incorrect colors
Fix: Use terminal with ANSI support
```

### Debug Mode

Enable in config.py for detailed logging:
```python
DEBUG_MODE = True
```

Check logs at: `logs/trunkr.log`

## Best Practices

1. **Regular Monitoring**
   - Keep terminal visible
   - Check all three panels
   - Monitor error messages

2. **Data Analysis**
   - Use color coding for quick analysis
   - Track patterns over time
   - Note unusual activities

3. **System Health**
   - Monitor connection status
   - Check update frequency
   - Verify data accuracy

## Additional Resources

- Check Architecture.md for system details
- Review Configuration.md for settings
- See Installation.md for setup help
