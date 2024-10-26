# Installation Guide

## Prerequisites

- Python 3.6 or higher
- Git (for version control)

## Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/LumenPrima/trunkr-monitor.git
cd trunkr-monitor
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install rich pymongo pytz
```

## Verification

To verify the installation:

1. Run the application:
```bash
python main.py
```

2. You should see a terminal interface with two panels:
   - Active Calls (left panel)
   - Recent Calls (right panel)

If you see the interface with the "Real-time Radio Call Monitor" message, the installation was successful.

## Notes

The following Python packages are required for the application to run:
- `rich`: For terminal user interface
- `pymongo`: For MongoDB database connectivity
- `pytz`: For timezone handling

These dependencies were determined through the application's import requirements and are all necessary for proper functionality.
