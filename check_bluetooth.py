#!/usr/bin/env python3
"""
Simple script to check if Bluetooth is available and working on macOS.
"""

import sys
import time
import objc
from Foundation import NSObject

try:
    import CoreBluetooth
except ImportError:
    print("Error: CoreBluetooth framework not found.")
    print("Please install PyObjC with: pip install pyobjc-framework-CoreBluetooth")
    sys.exit(1)

class BluetoothChecker(NSObject):
    """Simple class to check Bluetooth status."""
    
    def init(self):
        self = objc.super(BluetoothChecker, self).init()
        if self is None:
            return None
        self.state_updated = False
        return self
    
    def centralManagerDidUpdateState_(self, central):
        """Called when the central manager's state updates."""
        states = {
            CoreBluetooth.CBManagerStatePoweredOff: "Bluetooth is powered off",
            CoreBluetooth.CBManagerStatePoweredOn: "Bluetooth is powered on",
            CoreBluetooth.CBManagerStateResetting: "Bluetooth is resetting",
            CoreBluetooth.CBManagerStateUnauthorized: "Bluetooth is unauthorized",
            CoreBluetooth.CBManagerStateUnknown: "Bluetooth is unknown",
            CoreBluetooth.CBManagerStateUnsupported: "Bluetooth is not supported"
        }
        
        state = central.state()
        state_name = states.get(state, f"Unknown state code: {state}")
        print(f"Bluetooth state updated: {state_name}")
        
        if state == CoreBluetooth.CBManagerStatePoweredOn:
            print("✅ Bluetooth is working correctly!")
        elif state == CoreBluetooth.CBManagerStatePoweredOff:
            print("❌ Bluetooth is turned off. Please turn it on in System Settings.")
        elif state == CoreBluetooth.CBManagerStateUnauthorized:
            print("❌ Bluetooth access is unauthorized. Please grant Bluetooth permission to this application.")
        elif state == CoreBluetooth.CBManagerStateUnsupported:
            print("❌ Bluetooth is not supported on this device.")
        
        self.state_updated = True

def main():
    print("Checking Bluetooth status...")
    
    # Create the Bluetooth checker
    checker = BluetoothChecker.alloc().init()
    
    # Create the central manager
    central = CoreBluetooth.CBCentralManager.alloc().initWithDelegate_queue_(checker, None)
    
    # Print initial state
    state = central.state()
    states = {
        CoreBluetooth.CBManagerStatePoweredOff: "Bluetooth is powered off",
        CoreBluetooth.CBManagerStatePoweredOn: "Bluetooth is powered on",
        CoreBluetooth.CBManagerStateResetting: "Bluetooth is resetting",
        CoreBluetooth.CBManagerStateUnauthorized: "Bluetooth is unauthorized",
        CoreBluetooth.CBManagerStateUnknown: "Bluetooth is unknown",
        CoreBluetooth.CBManagerStateUnsupported: "Bluetooth is not supported"
    }
    print(f"Initial Bluetooth state: {states.get(state, f'Unknown state code: {state}')}")
    
    # Wait for state update if needed
    if state == CoreBluetooth.CBManagerStateUnknown:
        print("Waiting for Bluetooth state to be determined...")
        timeout = 5  # seconds
        start_time = time.time()
        
        while not checker.state_updated and time.time() - start_time < timeout:
            time.sleep(0.1)
        
        if not checker.state_updated:
            print("⚠️ Timeout waiting for Bluetooth state update.")
            print("This could indicate a problem with Bluetooth or permissions.")
    
    print("\nBluetooth Check Summary:")
    print("------------------------")
    if state == CoreBluetooth.CBManagerStatePoweredOn or (state == CoreBluetooth.CBManagerStateUnknown and checker.state_updated):
        print("✅ Bluetooth appears to be working correctly.")
        print("You should be able to run the Beacon Listener or BLE Scanner.")
    else:
        print("❌ Bluetooth is not ready for scanning.")
        print("Please check the following:")
        print("1. Bluetooth is turned on in System Settings")
        print("2. This application has permission to use Bluetooth")
        print("3. Your Mac has Bluetooth capability")
    
    print("\nFor more information, run the main beacon listener with:")
    print("python3 pyobjc.py")

if __name__ == "__main__":
    main() 