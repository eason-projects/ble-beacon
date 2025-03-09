# Beacon Listener for macOS

A Python program that uses PyObjC to listen for any iBeacon signals on macOS systems.

## Overview

This program leverages the Core Bluetooth and Core Location frameworks via PyObjC to detect and display information about nearby iBeacons. It's designed to work on macOS systems, including M4 MacBooks.

## Features

- Detects any iBeacon signals in the vicinity
- Displays detailed information about each detected beacon:
  - UUID
  - Major and Minor values
  - RSSI (signal strength)
  - Proximity (Immediate, Near, Far)
  - Estimated accuracy in meters
- Monitors for common iBeacon UUIDs used by various manufacturers
- Graceful error handling and status reporting

## Requirements

- macOS (tested on macOS 14 Sonoma)
- Python 3.6 or higher
- PyObjC package

## Installation

1. Make sure you have Python 3 installed on your system:
   ```bash
   python3 --version
   ```

2. Install the PyObjC package:
   ```bash
   pip install pyobjc
   ```

3. Download the `pyobjc.py` script from this repository.

## Usage

1. Run the script with Python 3:
   ```bash
   python3 pyobjc.py
   ```

2. The program will request location permissions when first run. You must grant "When In Use" or "Always" permission for the program to detect beacons.

3. The program will start scanning for Bluetooth devices and monitoring for iBeacons.

4. When an iBeacon is detected, information about the beacon will be displayed in the terminal.

5. Press Ctrl+C to stop the program.

## Permissions

This program requires the following permissions:

- Bluetooth access
- Location access (When In Use or Always)

On macOS, you'll be prompted to grant these permissions when the program is first run.

## How It Works

The program uses two main frameworks:

1. **Core Bluetooth** - For general Bluetooth device scanning
2. **Core Location** - For specific iBeacon detection and ranging

It monitors for several common iBeacon UUIDs used by various manufacturers, as well as a wildcard UUID to try to detect any iBeacon.

## Troubleshooting

- **No beacons detected**: Make sure Bluetooth is enabled on your Mac and that there are iBeacons broadcasting in your vicinity.
- **Permission errors**: Ensure you've granted the necessary permissions for Bluetooth and Location services.
- **Import errors**: Make sure PyObjC is properly installed with `pip install pyobjc`.

## Limitations

- This program can only detect iBeacons, not other types of Bluetooth beacons like Eddystone.
- Detection range is limited by Bluetooth hardware capabilities (typically 10-50 meters).
- The program must be running in the foreground to detect beacons.

## License

This project is open source and available under the MIT License. 