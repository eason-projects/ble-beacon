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