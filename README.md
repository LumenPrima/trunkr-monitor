# Trunkr Monitor

⚠️ **BETA PROJECT WARNING** ⚠️
This project is currently in BETA status and is NOT production-ready. Please note:
- Security features are incomplete and NOT suitable for production use
- Features are still under development and may change significantly
- Bugs and stability issues may exist
- No warranty or support is provided
- Use at your own risk

## Overview

Trunkr Monitor is a real-time monitoring system designed to work with [trunk-recorder](https://github.com/robotastic/trunk-recorder), extending its capabilities with advanced features like audio transcription and unit tracking. The system processes audio recordings and metadata from trunk-recorder, storing them in MongoDB and providing a terminal-based user interface for monitoring activities.

### Key Features

- Real-time call monitoring
- Unit activity tracking
- Audio transcription using Faster Whisper
- MongoDB integration for data storage
- Terminal-based UI with rich formatting
- Flexible deployment options (local, distributed, or cloud)

## Documentation

- [Installation Guide](docs/Installation.md) - Complete setup instructions
- [Configuration Guide](docs/Configuration.md) - Detailed configuration options
- [Architecture Guide](docs/Architecture.md) - System design and components
- [Usage Guide](docs/Usage.md) - How to use the system

## Components

### Core System
- Terminal-based monitoring interface
- MongoDB integration for data storage
- Real-time updates via change streams or polling
- Timezone-aware timestamp handling

### Audio Processing
- Integration with [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) for transcription
- Audio compression and storage
- Batch processing capabilities
- Optional transcription support

### Data Management
- MongoDB GridFS for audio storage
- Metadata collection management
- Unit activity tracking
- Call history maintenance

## Requirements

- Python 3.7+
- MongoDB
- trunk-recorder setup
- FFmpeg for audio processing
- Docker (for Faster Whisper Server)

## Quick Start

1. Install dependencies:
```bash
pip install rich pymongo pytz python-dotenv
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start the monitor:
```bash
python main.py
```

See the [Installation Guide](docs/Installation.md) for complete setup instructions.

## Deployment Options

### Local Development
- All components running locally
- Best for development and testing
- Easiest to set up and debug

### Distributed Setup
- MongoDB on dedicated server
- Faster Whisper on GPU machine
- Monitor on workstations
- Better for team environments

### Cloud-Based
- MongoDB Atlas for database
- Cloud-hosted Whisper API
- Monitor running locally
- Suitable for scalable deployments

## Scripts

The project includes several utility scripts:

- `process_audio_upload.sh` - Process and upload individual audio files
- `process_audio_upload_no_transcription.sh` - Process without transcription
- `batch_audio_processor.sh` - Batch process audio files
- `process_folder.sh` - Process entire folders of recordings
- `unit_script_logger.sh` - Log unit activities

## Integration with trunk-recorder

This project is designed to enhance [trunk-recorder](https://github.com/robotastic/trunk-recorder) by:
1. Processing its audio recordings and metadata
2. Adding transcription capabilities
3. Providing a real-time monitoring interface
4. Storing data in a queryable database
5. Tracking unit activities

Configure trunk-recorder to output to a directory monitored by this system for seamless integration.

## Contributing

This is a beta project under active development. Contributions are welcome:
- Bug reports
- Feature requests
- Code contributions
- Documentation improvements

## License

[Insert License Information]

## Acknowledgments

- [trunk-recorder](https://github.com/robotastic/trunk-recorder) - The foundation for this project
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) - Speech-to-text capabilities
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [PyMongo](https://github.com/mongodb/mongo-python-driver) - MongoDB integration
