from setuptools import setup
import os
import sys

# Add parent directory to path so we can import from scanner
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

APP = ['launcher.py']
DATA_FILES = [
    ('', ['../requirements.txt']),
    ('', ['../scan.py'])  # Changed to include scan.py in the root resources directory
]

OPTIONS = {
    'argv_emulation': False,  # Changed from True to False to avoid Carbon framework dependency
    'iconfile': 'app_icon.icns',  # You'll need to create this icon file
    'plist': {
        'CFBundleName': 'BLE Kafka Scanner',
        'CFBundleDisplayName': 'BLE Kafka Scanner',
        'CFBundleIdentifier': 'com.example.blekafkascanner',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSBluetoothAlwaysUsageDescription': 'This app needs Bluetooth to scan for BLE beacons.',
        'NSLocationWhenInUseUsageDescription': 'This app needs location services to detect BLE beacons.',
        'NSLocationAlwaysAndWhenInUseUsageDescription': 'This app needs location services to detect BLE beacons.',
        'NSLocationAlwaysUsageDescription': 'This app needs location services to detect BLE beacons.',
        'LSBackgroundOnly': False,
        'LSEnvironment': {
            'KAFKA_BROKER': 'localhost:9092',
            'KAFKA_TOPIC': 'ble_beacons'
        }
    },
    'packages': [
        'bleak', 
        'asyncio', 
        'kafka'
    ],
    'includes': [
        'json',
        'datetime',
        'uuid',
        'struct',
        'platform',
        'os',
        'socket',
        'time',
        'subprocess'
    ],
    'resources': [
        
    ]
}

setup(
    app=APP,
    name='BLE Kafka Scanner',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 