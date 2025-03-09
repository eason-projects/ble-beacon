# Bluetooth Beacon and BLE Scanner for macOS

This repository contains Python programs that use PyObjC to listen for Bluetooth Low Energy (BLE) advertisements on macOS systems, including iBeacons, Eddystone beacons, and other BLE devices.

## Programs Included

1. **iBeacon Listener (`pyobjc.py`)** - Specifically designed to detect and monitor iBeacon signals.
2. **BLE Scanner (`ble_scanner.py`)** - A more advanced scanner that can detect any type of BLE advertisement, including iBeacons, Eddystone beacons, and other BLE devices.

## Requirements

- macOS (tested on macOS 14 Sonoma)
- Python 3.6 or higher
- PyObjC package and related frameworks

## Installation

1. Make sure you have Python 3 installed on your system:
   ```bash
   python3 --version
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## iBeacon Listener (`pyobjc.py`)

### Features

- Detects iBeacon signals in the vicinity
- Displays detailed information about each detected beacon:
  - UUID
  - Major and Minor values
  - RSSI (signal strength)
  - Proximity (Immediate, Near, Far)
  - Estimated accuracy in meters
- Monitors for common iBeacon UUIDs used by various manufacturers

### Usage

```bash
python3 pyobjc.py
```

For more details, see [BEACON_README.md](BEACON_README.md).

## BLE Scanner (`ble_scanner.py`)

### Features

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

### Usage

```bash
python3 ble_scanner.py
```

For more details, see [BLE_README.md](BLE_README.md).

## Permissions

Both programs require:
- Bluetooth access permission
- For the iBeacon Listener, location permissions are also required

On macOS, you'll be prompted to grant these permissions when the programs are first run.

## How to Choose Which Program to Use

- Use **iBeacon Listener** (`pyobjc.py`) if you're specifically interested in iBeacons and want detailed proximity information.
- Use **BLE Scanner** (`ble_scanner.py`) if you want to detect all types of BLE advertisements, including but not limited to iBeacons.

## Troubleshooting

- **No devices detected**: Make sure Bluetooth is enabled on your Mac and that there are BLE devices broadcasting in your vicinity.
- **Permission errors**: Ensure you've granted the necessary permissions for Bluetooth and Location services.
- **Import errors**: Make sure PyObjC and related frameworks are properly installed with `pip install -r requirements.txt`.

## Limitations

- Detection range is limited by Bluetooth hardware capabilities (typically 10-50 meters).
- The programs must be running in the foreground to detect devices.
- Some manufacturer-specific data formats may not be fully decoded.

## License

This project is open source and available under the MIT License. 