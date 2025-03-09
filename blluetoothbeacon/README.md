# BLE Beacon Transmitter

This Android application broadcasts Bluetooth Low Energy (BLE) beacons that can be used for location testing. Other devices can receive these beacons and use the RSSI (Received Signal Strength Indicator) values to estimate proximity or location.

## Features

- Broadcasts iBeacon format BLE advertisements
- Configurable UUID, Major, Minor, and TX Power values
- Optional device name inclusion for easier identification
- Custom service UUID support for specialized applications
- Adjustable transmission power levels for different range requirements
- Configurable advertising modes for balancing detection speed and battery usage
- Simplified mode for devices with BLE advertising limitations
- Simple user interface to start/stop beacon transmission
- Real-time status indicator

## Requirements

- Android device with Bluetooth Low Energy support
- Android SDK 34 or higher
- Bluetooth and Location permissions

## Usage

1. Install the app on your Android device
2. Grant the required Bluetooth and Location permissions
3. Enable Bluetooth if not already enabled
4. Configure the beacon parameters (or use the defaults):
   - UUID: A unique identifier for your beacon network
   - Major: A value to identify a group of beacons
   - Minor: A value to identify a specific beacon
   - TX Power: The signal power measured at 1 meter from the device (in dBm)
5. Configure identification options (optional):
   - Include Device Name: Makes your beacon more easily identifiable in scanner apps
   - Custom Service UUID: Allows specialized applications to filter for your beacon
   - Simplified Mode: Use this if your device has BLE advertising limitations
6. Configure transmission options:
   - Power Level: Select from Ultra Low (-21 dBm) to High (0 dBm)
   - Advertising Mode: Choose between Low Power (1000ms), Balanced (250ms), or Low Latency (100ms)
7. Tap "Start Beacon" to begin broadcasting
8. Tap "Stop Beacon" to end broadcasting

## Simplified Mode

Some Android devices have limitations on the size of BLE advertising data they can transmit. If you encounter a "Data Too Large" error when starting the beacon, the app will offer to switch to simplified mode.

Simplified mode:
- Disables device name broadcasting
- Removes service UUID from the advertisement
- Uses only the essential iBeacon data (UUID, Major, Minor, TX Power)
- Maintains the selected power level and advertising mode

You can also enable simplified mode manually by checking the "Simplified Mode" option in the Identification Options section.

## Transmission Power Levels

The app offers four transmission power levels:

- **Ultra Low (-21 dBm)**: Shortest range, lowest power consumption
- **Low (-15 dBm)**: Short range, low power consumption
- **Medium (-7 dBm)**: Medium range, moderate power consumption
- **High (0 dBm)**: Maximum range, highest power consumption

Higher power levels increase the detection range but consume more battery. Choose the appropriate level based on your testing requirements.

## Advertising Modes

The app offers three advertising modes that control how frequently the beacon broadcasts:

- **Low Power (1000ms)**: Broadcasts every 1000ms, lowest power consumption
- **Balanced (250ms)**: Broadcasts every 250ms, moderate power consumption
- **Low Latency (100ms)**: Broadcasts every 100ms, highest power consumption

More frequent broadcasting (lower latency) allows for faster detection but uses more battery power.

## Testing

To test the beacon:

1. Use another device with a BLE scanner app (like "nRF Connect" or "Beacon Scanner")
2. Scan for BLE devices or iBeacons
3. The scanner should detect your beacon and display its information
4. If you enabled the device name option, your beacon will appear with the specified name
5. The RSSI value shown in the scanner indicates the signal strength, which correlates to distance
6. Try different power levels to see how they affect the detection range and RSSI values

## Technical Details

- The app uses the standard Android Bluetooth LE Advertising API
- Beacon format follows the iBeacon specification
- Default UUID: E2C56DB5-DFFB-48D2-B060-D0F5A71096E0
- Default Major: 1
- Default Minor: 100
- Default TX Power: -59 dBm
- Default Service UUID (when using custom identification): 0000FFFF-0000-1000-8000-00805F9B34FB

## Identification Methods

The app supports multiple ways to make your beacon identifiable:

1. **iBeacon Parameters**: The standard UUID, Major, and Minor values
2. **Device Name**: When enabled, your beacon will broadcast with a friendly name
3. **Service UUID**: A custom UUID that can be used to filter for your specific beacon type

## Troubleshooting

- **"Data Too Large" Error**: If you see this error, your device has limitations on the size of BLE advertising data. Use simplified mode to resolve this issue.
- **No Beacon Detected**: Make sure Bluetooth is enabled on both devices and that you're using a compatible scanner app.
- **Device Name Not Visible**: Some scanner apps don't display device names. Try using nRF Connect or another app that specifically shows device names.
- **Limited Range**: If you're not seeing the expected range with higher power levels, check if your device supports the selected power level or try a different device.
- **Beacon Stops Broadcasting**: Some Android devices may stop broadcasting after a period of time due to battery optimization. Keep the app in the foreground or disable battery optimization for the app.
- **General Issues**: If the beacon doesn't start, ensure Bluetooth is enabled and permissions are granted.
- **Compatibility Issues**: Some Android devices may have limitations on BLE advertising capabilities. Try simplified mode if you encounter problems.

## License

This project is open source and available under the MIT License. 