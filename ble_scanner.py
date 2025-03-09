#!/usr/bin/env python3
"""
BLE Scanner - A Python program to listen for any Bluetooth Low Energy advertisements
on macOS systems.

This script uses Core Bluetooth framework via PyObjC to detect and display information
about nearby BLE devices, including iBeacons and other advertisement types.
"""

import time
import binascii
import objc
from Foundation import (
    NSObject,
    NSLog,
    NSData,
    NSUUID
)

# Import Core Bluetooth framework
try:
    import CoreBluetooth
except ImportError:
    print("Error: Required frameworks not found. Please install PyObjC:")
    print("pip install pyobjc")
    exit(1)

class CentralManagerDelegate(NSObject):
    """Delegate for handling Core Bluetooth central manager events."""
    
    def initWithCallback_(self, callback):
        self = objc.super(CentralManagerDelegate, self).init()
        if self is None:
            return None
        self.callback = callback
        self.discovered_devices = {}
        return self
    
    def centralManagerDidUpdateState_(self, central):
        states = {
            CoreBluetooth.CBManagerStatePoweredOff: "Bluetooth is powered off",
            CoreBluetooth.CBManagerStatePoweredOn: "Bluetooth is powered on",
            CoreBluetooth.CBManagerStateResetting: "Bluetooth is resetting",
            CoreBluetooth.CBManagerStateUnauthorized: "Bluetooth is unauthorized",
            CoreBluetooth.CBManagerStateUnknown: "Bluetooth state is unknown",
            CoreBluetooth.CBManagerStateUnsupported: "Bluetooth is not supported"
        }
        
        state = central.state()
        print(f"Bluetooth state: {states.get(state, 'Unknown')}")
        
        if state == CoreBluetooth.CBManagerStatePoweredOn:
            print("Bluetooth is ready, starting scan...")
            self.callback("bluetooth_ready")
        else:
            print("Bluetooth is not ready for scanning")
    
    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, central, peripheral, advertisementData, RSSI):
        """Called when a peripheral is discovered."""
        # Get device information
        device_id = peripheral.identifier().UUIDString()
        device_name = peripheral.name() or "Unknown"
        
        # Check if this is a new device or has updated data
        is_new = device_id not in self.discovered_devices
        
        # Store or update device information
        self.discovered_devices[device_id] = {
            'name': device_name,
            'rssi': RSSI,
            'peripheral': peripheral,
            'advertisement_data': advertisementData,
            'last_seen': time.time()
        }
        
        # Process the advertisement data
        self.process_advertisement_data(device_id, device_name, advertisementData, RSSI, is_new)
    
    def process_advertisement_data(self, device_id, device_name, advertisementData, RSSI, is_new):
        """Process the advertisement data from a peripheral."""
        # Print basic device information
        if is_new:
            print(f"\n=== NEW DEVICE DISCOVERED ===")
        else:
            print(f"\n=== UPDATED DEVICE DATA ===")
        
        print(f"Device ID: {device_id}")
        print(f"Device Name: {device_name}")
        print(f"RSSI: {RSSI} dBm")
        
        # Process advertisement data
        print("Advertisement Data:")
        
        # Check for manufacturer data (which could include iBeacon data)
        if CoreBluetooth.CBAdvertisementDataManufacturerDataKey in advertisementData:
            mfg_data = advertisementData[CoreBluetooth.CBAdvertisementDataManufacturerDataKey]
            mfg_bytes = bytes(mfg_data)
            
            print(f"  Manufacturer Data: {binascii.hexlify(mfg_bytes).decode('utf-8')}")
            
            # Check if this is an iBeacon
            if len(mfg_bytes) >= 25 and mfg_bytes[0:2] == b'\x4C\x00' and mfg_bytes[2:4] == b'\x02\x15':
                # This is an iBeacon
                uuid_bytes = mfg_bytes[4:20]
                uuid_string = '-'.join([
                    binascii.hexlify(uuid_bytes[0:4]).decode('utf-8'),
                    binascii.hexlify(uuid_bytes[4:6]).decode('utf-8'),
                    binascii.hexlify(uuid_bytes[6:8]).decode('utf-8'),
                    binascii.hexlify(uuid_bytes[8:10]).decode('utf-8'),
                    binascii.hexlify(uuid_bytes[10:16]).decode('utf-8')
                ])
                
                major = int.from_bytes(mfg_bytes[20:22], byteorder='big')
                minor = int.from_bytes(mfg_bytes[22:24], byteorder='big')
                tx_power = int.from_bytes(mfg_bytes[24:25], byteorder='big', signed=True)
                
                print("  ** iBeacon Data **")
                print(f"  UUID: {uuid_string.upper()}")
                print(f"  Major: {major}")
                print(f"  Minor: {minor}")
                print(f"  Tx Power: {tx_power} dBm")
                
                # Calculate approximate distance
                if RSSI != 0 and tx_power != 0:
                    # Simple distance calculation (rough estimate)
                    ratio = RSSI / tx_power
                    if ratio < 1.0:
                        distance = ratio**10
                    else:
                        distance = 0.89976 * (ratio**7.7095) + 0.111
                    print(f"  Estimated Distance: {distance:.2f} meters")
        
        # Check for service UUIDs
        if CoreBluetooth.CBAdvertisementDataServiceUUIDsKey in advertisementData:
            service_uuids = advertisementData[CoreBluetooth.CBAdvertisementDataServiceUUIDsKey]
            if service_uuids:
                print("  Service UUIDs:")
                for uuid in service_uuids:
                    print(f"    {uuid}")
        
        # Check for local name (which might be different from peripheral name)
        if CoreBluetooth.CBAdvertisementDataLocalNameKey in advertisementData:
            local_name = advertisementData[CoreBluetooth.CBAdvertisementDataLocalNameKey]
            print(f"  Local Name: {local_name}")
        
        # Check for service data
        if CoreBluetooth.CBAdvertisementDataServiceDataKey in advertisementData:
            service_data = advertisementData[CoreBluetooth.CBAdvertisementDataServiceDataKey]
            print("  Service Data:")
            for uuid, data in service_data.items():
                data_bytes = bytes(data)
                print(f"    {uuid}: {binascii.hexlify(data_bytes).decode('utf-8')}")
                
                # Check for Eddystone format
                if str(uuid).upper() == "FEAA":  # Eddystone service UUID
                    self.process_eddystone(data_bytes)
        
        # Check for TX power level
        if CoreBluetooth.CBAdvertisementDataTxPowerLevelKey in advertisementData:
            tx_power = advertisementData[CoreBluetooth.CBAdvertisementDataTxPowerLevelKey]
            print(f"  TX Power Level: {tx_power} dBm")
        
        # Check if device is connectable
        if CoreBluetooth.CBAdvertisementDataIsConnectable in advertisementData:
            connectable = advertisementData[CoreBluetooth.CBAdvertisementDataIsConnectable]
            print(f"  Connectable: {'Yes' if connectable else 'No'}")
        
        # Check for solicited service UUIDs
        if CoreBluetooth.CBAdvertisementDataSolicitedServiceUUIDsKey in advertisementData:
            solicited_uuids = advertisementData[CoreBluetooth.CBAdvertisementDataSolicitedServiceUUIDsKey]
            if solicited_uuids:
                print("  Solicited Service UUIDs:")
                for uuid in solicited_uuids:
                    print(f"    {uuid}")
        
        print("==============================")
    
    def process_eddystone(self, data_bytes):
        """Process Eddystone beacon data."""
        if len(data_bytes) < 1:
            return
        
        frame_type = data_bytes[0]
        print("  ** Eddystone Beacon **")
        
        if frame_type == 0x00:  # Eddystone-UID
            if len(data_bytes) >= 18:
                tx_power = int.from_bytes([data_bytes[1]], byteorder='big', signed=True)
                namespace = binascii.hexlify(data_bytes[2:12]).decode('utf-8')
                instance = binascii.hexlify(data_bytes[12:18]).decode('utf-8')
                print(f"  Eddystone-UID")
                print(f"  TX Power: {tx_power} dBm")
                print(f"  Namespace: {namespace.upper()}")
                print(f"  Instance: {instance.upper()}")
        
        elif frame_type == 0x10:  # Eddystone-URL
            if len(data_bytes) >= 3:
                tx_power = int.from_bytes([data_bytes[1]], byteorder='big', signed=True)
                url_scheme = ["http://www.", "https://www.", "http://", "https://"][data_bytes[2]]
                url_encoded = data_bytes[3:]
                
                # Decode URL
                url = url_scheme
                for b in url_encoded:
                    if b <= 13:
                        url += [".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
                               ".com", ".org", ".edu", ".net", ".info", ".biz", ".gov"][b]
                    else:
                        url += chr(b)
                
                print(f"  Eddystone-URL")
                print(f"  TX Power: {tx_power} dBm")
                print(f"  URL: {url}")
        
        elif frame_type == 0x20:  # Eddystone-TLM
            if len(data_bytes) >= 14:
                version = data_bytes[1]
                battery = int.from_bytes(data_bytes[2:4], byteorder='big')
                temperature = int.from_bytes(data_bytes[4:6], byteorder='big') / 256.0
                pdu_count = int.from_bytes(data_bytes[6:10], byteorder='big')
                time_since_boot = int.from_bytes(data_bytes[10:14], byteorder='big') / 10.0
                
                print(f"  Eddystone-TLM")
                print(f"  Version: {version}")
                print(f"  Battery: {battery} mV")
                print(f"  Temperature: {temperature:.2f}°C")
                print(f"  PDU Count: {pdu_count}")
                print(f"  Time since boot: {time_since_boot:.1f} seconds")
        
        elif frame_type == 0x30:  # Eddystone-EID
            if len(data_bytes) >= 9:
                tx_power = int.from_bytes([data_bytes[1]], byteorder='big', signed=True)
                eid = binascii.hexlify(data_bytes[2:10]).decode('utf-8')
                
                print(f"  Eddystone-EID")
                print(f"  TX Power: {tx_power} dBm")
                print(f"  EID: {eid.upper()}")

class BLEScanner:
    """Main class for scanning BLE advertisements."""
    
    def __init__(self):
        # Create Core Bluetooth central manager
        self.central_delegate = CentralManagerDelegate.alloc().initWithCallback_(self.handle_event)
        self.central_manager = CoreBluetooth.CBCentralManager.alloc().initWithDelegate_queue_(
            self.central_delegate, None
        )
        
        print("BLE Scanner initialized")
        print("Waiting for Bluetooth to be ready...")
    
    def handle_event(self, event_type, *args, **kwargs):
        """Handle events from the delegate."""
        if event_type == "bluetooth_ready":
            self.start_scanning()
    
    def start_scanning(self):
        """Start scanning for BLE devices."""
        scan_options = {
            CoreBluetooth.CBCentralManagerScanOptionAllowDuplicatesKey: True
        }
        self.central_manager.scanForPeripheralsWithServices_options_(None, scan_options)
        print("Scanning for BLE devices...")
    
    def stop(self):
        """Stop scanning."""
        self.central_manager.stopScan()
        print("Stopped scanning")

def main():
    print("Starting BLE Scanner...")
    print("This program will listen for any Bluetooth Low Energy advertisements.")
    print("Press Ctrl+C to exit.")
    
    scanner = BLEScanner()
    
    try:
        # Keep the program running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping BLE Scanner...")
        scanner.stop()
        print("BLE Scanner stopped.")

if __name__ == "__main__":
    main() 