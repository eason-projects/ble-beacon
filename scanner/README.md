# BLE to Kafka Integration

This project scans for Bluetooth Low Energy (BLE) beacons and sends the data to a Kafka topic.

## Prerequisites

- Python 3.7+
- Kafka server running on localhost:9092
- Required Python packages (install with `pip install -r requirements.txt`):
  - bleak
  - kafka-python

## Setup

1. Make sure Kafka is running. You can use the provided Docker Compose setup:

```bash
cd kafka
docker-compose up -d
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Scanner

Run the BLE scanner with:

```bash
python scanner/scan.py
```

The scanner will:
1. Scan for BLE beacons (iBeacon, Eddystone, AltBeacon)
2. Print the detected beacons to the console
3. Send the beacon data to the Kafka topic `ble_beacons`

## Kafka Data Format

The data sent to Kafka is in JSON format with the following structure:

### iBeacon
```json
{
  "type": "iBeacon",
  "uuid": "string",
  "major": integer,
  "minor": integer,
  "rssi": integer,
  "address": "string",
  "name": "string",
  "host_id": "string",
  "timestamp": "ISO-8601 timestamp"
}
```

### Eddystone
```json
{
  "type": "Eddystone-UID|Eddystone-URL|Eddystone-TLM",
  "address": "string",
  "rssi": integer,
  "name": "string",
  "host_id": "string",
  "timestamp": "ISO-8601 timestamp"
}
```

### AltBeacon
```json
{
  "type": "AltBeacon",
  "id": "string",
  "rssi": integer,
  "address": "string",
  "name": "string",
  "host_id": "string",
  "timestamp": "ISO-8601 timestamp"
}
```

## Viewing Kafka Messages

You can use the Kafka UI to view messages:

1. Access the Kafka UI at http://localhost:9080
2. Navigate to the "Topics" section
3. Select the `ble_beacons` topic
4. View the messages in the "Messages" tab

## Troubleshooting

If you encounter issues connecting to Kafka:

1. Ensure Kafka is running: `docker ps | grep broker`
2. Check Kafka logs: `docker logs broker`
3. Verify network connectivity: `telnet localhost 9092`

## Compatibility Issues

### Carbon Framework Error

If you encounter the following error when running the application on newer macOS versions:

```
OSError: dlopen(/System/Library/Carbon.framework/Carbon, 0x0006): tried: '/System/Library/Carbon.framework/Carbon' (no such file), '/System/Volumes/Preboot/Cryptexes/OS/System/Library/Carbon.framework/Carbon' (no such file), '/System/Library/Carbon.framework/Carbon' (no such file, not in dyld cache)
```

This is because the application is trying to use the Carbon framework, which is deprecated and may not be available on newer macOS versions, especially on Apple Silicon Macs.

### Rebuilding the Application

To fix this issue, you need to rebuild the application with the updated configuration:

1. Clone the repository
2. Navigate to the installer directory
3. Run the following commands:

```bash
# Install dependencies
./install_build_deps.sh

# Build the application
./build_macos_installer.sh
```

This will create a new DMG file in the root directory that should be compatible with newer macOS versions.

### Technical Details

The issue is related to the `argv_emulation` option in py2app, which depends on the Carbon framework. The updated configuration explicitly disables this option and adds additional settings to avoid Carbon framework dependency. 