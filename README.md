# BLE Beacon System

A comprehensive Bluetooth Low Energy (BLE) beacon system that includes components for both transmitting and receiving beacon signals, with Kafka integration for data processing.

## Project Overview

This project consists of three main components:

1. **BLE Scanner** - A Python application that scans for BLE beacons and sends the data to Kafka
2. **Kafka Setup** - A Docker Compose configuration for setting up a Kafka environment
3. **BLE Beacon Transmitter** - An Android application that broadcasts BLE beacons

## Components

### 1. BLE Scanner (`/scanner`)

A Python application that scans for Bluetooth Low Energy (BLE) beacons and sends the data to a Kafka topic.

#### Features
- Detects multiple beacon formats (iBeacon, Eddystone, AltBeacon)
- Sends beacon data to Kafka in JSON format
- Includes a simple GUI for visualization

#### Requirements
- Python 3.7+
- Required packages: bleak, kafka-python, Pillow, wxPython

#### Usage
```bash
cd scanner
pip install -r requirements.txt
python scan.py
```

For more details, see the [Scanner README](scanner/README.md).

### 2. Kafka Setup (`/kafka`)

A Docker Compose configuration for setting up a simple Kafka environment with the following components:
- Kafka broker (running in KRaft mode without Zookeeper)
- Kafka UI (web interface for managing Kafka)

#### Requirements
- Docker and Docker Compose

#### Usage
```bash
cd kafka
docker-compose up -d
```

Access the Kafka UI at http://localhost:8080

For more details, see the [Kafka README](kafka/README.md).

### 3. BLE Beacon Transmitter (`/blluetoothbeacon`)

An Android application that broadcasts Bluetooth Low Energy (BLE) beacons that can be used for location testing.

#### Features
- Broadcasts iBeacon format BLE advertisements
- Configurable UUID, Major, Minor, and TX Power values
- Adjustable transmission power levels and advertising modes
- Simple user interface to start/stop beacon transmission

#### Requirements
- Android device with Bluetooth Low Energy support
- Android SDK 34 or higher
- Bluetooth and Location permissions

For more details, see the [BLE Beacon Transmitter README](blluetoothbeacon/README.md).

## System Architecture

The system works as follows:

1. The Android app broadcasts BLE beacon signals
2. The Python scanner detects these signals and other BLE beacons in the vicinity
3. The scanner sends the beacon data to Kafka
4. Kafka stores the data and makes it available for further processing

This architecture allows for real-time tracking and analysis of BLE beacon data.

## Getting Started

### Prerequisites
- Python 3.7+
- Docker and Docker Compose
- Android Studio (for building the Android app)

### Setup Steps

1. Start the Kafka environment:
```bash
cd kafka
docker-compose up -d
```

2. Run the BLE scanner:
```bash
cd scanner
pip install -r requirements.txt
python scan.py
```

3. Build and install the Android app:
```bash
cd blluetoothbeacon
./gradlew installDebug
```

## Data Format

The beacon data sent to Kafka is in JSON format with structures specific to each beacon type (iBeacon, Eddystone, AltBeacon). See the [Scanner README](scanner/README.md) for detailed format specifications.

## Troubleshooting

### Scanner Issues
- If you encounter Carbon Framework errors on newer macOS versions, see the troubleshooting section in the [Scanner README](scanner/README.md).

### Kafka Issues
- For Kafka connection issues, see the troubleshooting section in the [Kafka README](kafka/README.md).

### Android App Issues
- For "Data Too Large" errors or other beacon transmission issues, see the troubleshooting section in the [BLE Beacon Transmitter README](blluetoothbeacon/README.md).

## License

This project is open source for non-commercial use only. Commercial use of this project or any of its components requires explicit permission from the author. You are free to use, modify, and distribute this software for personal, educational, research, or other non-commercial purposes, provided appropriate attribution is given.

For commercial licensing inquiries, please contact the author.
