from setuptools import setup

APP = ['pyobjc.py']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': 'BeaconListener',
        'CFBundleDisplayName': 'Beacon Listener',
        'CFBundleIdentifier': 'com.example.beaconlistener',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSBluetoothAlwaysUsageDescription': 'This app needs Bluetooth to scan for iBeacons.',
        'NSLocationWhenInUseUsageDescription': 'This app needs location services to detect iBeacons.',
        'NSLocationAlwaysAndWhenInUseUsageDescription': 'This app needs location services to detect iBeacons.',
        'NSLocationAlwaysUsageDescription': 'This app needs location services to detect iBeacons.',
        'LSBackgroundOnly': False,
    },
    'packages': ['CoreBluetooth', 'CoreLocation'],
}

setup(
    app=APP,
    name='BeaconListener',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 