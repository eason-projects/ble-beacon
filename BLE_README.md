# BLE Scanner for macOS

A Python program that uses PyObjC to listen for any Bluetooth Low Energy (BLE) advertisements on macOS systems, including iBeacons, Eddystone beacons, and other BLE devices.

## Overview

This program leverages the Core Bluetooth framework via PyObjC to detect and display detailed information about nearby BLE devices. It's designed to work on macOS systems, including M4 MacBooks, and can detect any type of BLE advertisement, not just iBeacons.

## Features

- Detects any BLE advertisement signals in the vicinity
- Identifies and parses different beacon formats:
  - iBeacon (Apple's beacon format)
  - Eddystone (Google's beacon format) including UID, URL, TLM, and EID frame types
- Displays detailed information about each detected device:
  - Device ID and name
  - RSSI (signal strength)
  - Manufacturer data
  - Service UUIDs
  - Service data
  - TX power level
  - Connectable status
  - And more...
- For iBeacons, displays:
  - UUID
  - Major and Minor values
  - Estimated distance
- For Eddystone beacons, displays format-specific data:
  - UID: Namespace and Instance IDs
  - URL: Decoded web URL
  - TLM: Battery, temperature, and other telemetry data
  - EID: Ephemeral Identifier

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

3. Download the `ble_scanner.py` script from this repository.

## Usage

1. Run the script with Python 3:
   ```bash
   python3 ble_scanner.py
   ```

2. The program will request Bluetooth permissions when first run. You must grant permission for the program to detect BLE devices.

3. The program will start scanning for BLE devices and display information about each detected device in the terminal.

4. Press Ctrl+C to stop the program.

## Permissions

This program requires Bluetooth access permission. On macOS, you'll be prompted to grant this permission when the program is first run.

## How It Works

The program uses the Core Bluetooth framework to scan for BLE advertisements. When a device is discovered, it:

1. Extracts basic device information (ID, name, RSSI)
2. Parses the advertisement data to identify the device type
3. For known beacon types (iBeacon, Eddystone), extracts and displays format-specific information
4. For iBeacons, calculates an estimated distance based on RSSI and TX power

The program continuously scans for devices and updates the display when new devices are found or when existing devices broadcast updated information.

## Troubleshooting

- **No devices detected**: Make sure Bluetooth is enabled on your Mac and that there are BLE devices broadcasting in your vicinity.
- **Permission errors**: Ensure you've granted the necessary permissions for Bluetooth.
- **Import errors**: Make sure PyObjC is properly installed with `pip install pyobjc`.

## Limitations

- Detection range is limited by Bluetooth hardware capabilities (typically 10-50 meters).
- The program must be running in the foreground to detect devices.
- Some manufacturer-specific data formats may not be fully decoded.

## Advanced Usage

### Filtering Devices

To modify the script to filter for specific devices, you can edit the `process_advertisement_data` method in the `CentralManagerDelegate` class to add filtering logic based on:

- Device name
- UUID
- Manufacturer data
- Signal strength (RSSI)

### Logging Data

To log the detected devices to a file, you can modify the script to write the device information to a file instead of (or in addition to) printing it to the console.

## License

This project is open source and available under the MIT License. 