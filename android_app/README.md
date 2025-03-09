# Bluetooth Beacon Broadcaster

An Android application for broadcasting Bluetooth Low Energy (BLE) signals with customizable settings.

## Features

- Broadcast BLE signals with a custom UUID
- Adjust transmission power (Ultra Low, Low, Medium, High)
- Configure advertising mode (Low Power, Balanced, Low Latency)
- Save and load presets for quick configuration
- Real-time status updates

## Requirements

- Android device with Bluetooth Low Energy support
- Android 6.0 (Marshmallow) or higher
- Location permissions (required for Bluetooth scanning on Android)
- For Android 12+: BLUETOOTH_ADVERTISE and BLUETOOTH_CONNECT permissions

## How to Use

1. **Install the App**: Install the app on your Android device.

2. **Grant Permissions**: When prompted, grant the necessary permissions for Bluetooth and location.

3. **Configure Broadcast Settings**:
   - **UUID**: Enter a valid UUID in the format `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`
   - **Transmission Power**: Select the desired power level
     - Ultra Low: Lowest power, shortest range
     - Low: Reduced power, shorter range
     - Medium: Balanced power and range
     - High: Maximum power and range
   - **Advertising Mode**: Select the desired mode
     - Low Power: Conserves battery but has higher latency
     - Balanced: Moderate power consumption and latency
     - Low Latency: Highest power consumption but lowest latency

4. **Start Broadcasting**: Tap the "Start Broadcasting" button to begin transmitting the BLE signal.

5. **Stop Broadcasting**: Tap the "Stop Broadcasting" button to cease transmission.

6. **Save Presets**: Configure your settings, then tap "Save" to store the current configuration as a preset.

7. **Load Presets**: Select a saved preset from the dropdown menu to quickly load a configuration.

## Power Consumption Notes

- Higher transmission power and lower latency settings will consume more battery
- For long-term broadcasting, consider using Low Power mode with Medium or Low transmission power
- The app will automatically stop broadcasting when it's in the background to conserve battery

## Troubleshooting

- If broadcasting fails to start, ensure Bluetooth is enabled on your device
- Some devices may not support Bluetooth LE advertising
- For Android 12+, ensure all required permissions are granted
- If the UUID is invalid, the app will notify you

## Use Cases

- Indoor positioning systems
- Asset tracking
- Proximity marketing
- IoT device communication
- Location-based services

## Privacy and Security

- Broadcasting a Bluetooth signal makes your device discoverable to nearby devices
- Consider using a random UUID for privacy concerns
- The app does not collect or transmit any personal data

## License

This application is open source and available under the MIT License. 