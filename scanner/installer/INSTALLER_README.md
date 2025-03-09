# BLE Kafka Scanner - macOS Installer

This document provides instructions for building and using the macOS installer for the BLE Kafka Scanner application.

## Prerequisites

Before building the installer, ensure you have the following installed:

- macOS 10.15 or later
- Python 3.7 or later
- Homebrew (for installing create-dmg)
- Xcode Command Line Tools

## Building the Installer

1. Make sure all dependencies are installed:

```bash
# Navigate to the installer directory
cd scanner/installer

# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python dependencies
pip install -r ../../requirements.txt

# Install py2app and create-dmg
pip install py2app
brew install create-dmg
```

2. Run the build script:

```bash
# Make the script executable
chmod +x install_build_deps.sh build_macos_installer.sh

# Install dependencies
./install_build_deps.sh

# Build the installer
./build_macos_installer.sh
```

3. The script will:
   - Install necessary build tools if they're missing
   - Create a placeholder app icon if one doesn't exist
   - Build the application using py2app
   - Package the application into a DMG installer

4. When the build is complete, you'll find `BLE Kafka Scanner.dmg` in the root directory of the project.

## Installing the Application

1. Double-click the `BLE Kafka Scanner.dmg` file to mount it
2. Drag the `BLE Kafka Scanner.app` to your Applications folder
3. Eject the DMG

## Running the Application

1. Open the `BLE Kafka Scanner.app` from your Applications folder
2. The first time you run it, macOS may show security warnings:
   - Go to System Preferences > Security & Privacy
   - Click "Open Anyway" to allow the app to run
3. The app will request permissions for:
   - Bluetooth access
   - Location services
   - Network access (for Kafka)

## Configuration

The application uses the following environment variables, which can be modified:

- `KAFKA_BROKER`: The Kafka broker address (default: localhost:9092)
- `KAFKA_TOPIC`: The Kafka topic to send data to (default: ble_beacons)

To change these settings, you can:

1. Edit the `scanner/installer/ble_kafka_setup.py` file before building
2. Set environment variables before launching the app

## Troubleshooting

If you encounter issues:

1. **App won't open due to security settings**:
   - Right-click the app and select "Open"
   - Click "Open" in the dialog that appears

2. **Bluetooth permissions issues**:
   - Go to System Preferences > Security & Privacy > Privacy > Bluetooth
   - Ensure BLE Kafka Scanner is allowed

3. **Location permissions issues**:
   - Go to System Preferences > Security & Privacy > Privacy > Location Services
   - Ensure BLE Kafka Scanner is allowed

4. **Kafka connection issues**:
   - Ensure Kafka is running at the configured address
   - Check network settings and firewall rules

## Creating a Universal Binary

The build script already creates a universal binary that works on both Intel and Apple Silicon Macs by using the `--arch=universal2` flag:

```bash
python ble_kafka_setup.py py2app --arch=universal2
```

This creates a universal binary that runs natively on both Intel and Apple Silicon Macs. 