#!/usr/bin/env python3
"""
BLE Kafka Scanner Launcher
--------------------------
This script launches the BLE Kafka Scanner application.
It handles permissions and configuration before starting the scanner.
"""

import os
import sys
import asyncio
import subprocess
import time
import platform

# Add resource paths for bundled application
def setup_paths():
    # When running as a bundled app, the resources are in a different location
    if getattr(sys, 'frozen', False):
        # Running as a bundled app
        bundle_dir = os.path.dirname(sys.executable)
        # Go up to the Resources directory
        resources_dir = os.path.abspath(os.path.join(bundle_dir, '..', 'Resources'))
        sys.path.insert(0, resources_dir)
    else:
        # Running in development mode
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Set up paths before importing other modules
setup_paths()

def check_permissions():
    """Check if the application has the necessary permissions."""
    print("Checking permissions...")
    
    # Check if we're on macOS
    if platform.system() != "Darwin":
        print("Warning: This application is designed for macOS.")
        return
    
    # Check Bluetooth permissions
    try:
        # This will prompt for Bluetooth permissions if not already granted
        subprocess.run(["blueutil", "-p", "1"], check=False, capture_output=True)
    except FileNotFoundError:
        print("Warning: blueutil not found. Cannot check Bluetooth status.")
    
    # Location permissions will be requested by CoreLocation when needed
    print("Permission checks completed.")

def main():
    """Main entry point for the application."""
    print("Starting BLE Kafka Scanner...")
    
    # Set up environment variables if not already set
    if 'KAFKA_BROKER' not in os.environ:
        os.environ['KAFKA_BROKER'] = 'localhost:9092'
    if 'KAFKA_TOPIC' not in os.environ:
        os.environ['KAFKA_TOPIC'] = 'ble_beacons'
    
    print(f"Kafka Broker: {os.environ['KAFKA_BROKER']}")
    print(f"Kafka Topic: {os.environ['KAFKA_TOPIC']}")
    
    # Check permissions
    check_permissions()
    
    try:
        # Import the scanner module
        from scan import scan_ble_devices
        
        # Run the scanner
        print("Starting BLE scanner...")
        asyncio.run(scan_ble_devices())
    except ImportError as e:
        print(f"Error importing scanner module: {e}")
        print(f"Python path: {sys.path}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"Error running scanner: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 