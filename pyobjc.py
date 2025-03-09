#!/usr/bin/env python3
"""
Beacon Listener - A Python program to listen for any iBeacon signals using PyObjC
on macOS systems.

This script uses Core Bluetooth and Core Location frameworks via PyObjC to detect
and display information about nearby iBeacons.
"""

import time
import objc
from Foundation import (
    NSObject,
    NSLog,
    NSUUID
)

# Import Core Bluetooth and Core Location frameworks
try:
    import CoreBluetooth
    import CoreLocation
except ImportError:
    print("Error: Required frameworks not found. Please install PyObjC:")
    print("pip install pyobjc")
    exit(1)

class CentralManagerDelegate(NSObject):
    """Delegate for handling Core Bluetooth central manager events."""
    
    def initWithListener_(self, listener):
        self = objc.super(CentralManagerDelegate, self).init()
        if self is None:
            return None
        self.listener = listener
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
        print(f"DEBUG: centralManagerDidUpdateState_ called with state: {state}")
        print(f"Bluetooth state: {states.get(state, 'Unknown')}")
        
        if state == CoreBluetooth.CBManagerStatePoweredOn:
            print("Bluetooth is ready, starting scan...")
            self.listener.start_scanning()
        else:
            print("Bluetooth is not ready for scanning")
            if state == CoreBluetooth.CBManagerStatePoweredOff:
                print("Please turn on Bluetooth in System Settings and try again.")
            elif state == CoreBluetooth.CBManagerStateUnauthorized:
                print("Please grant Bluetooth permission to this application.")
    
    # Ensure the method is properly registered with the Objective-C runtime
    centralManagerDidUpdateState_ = objc.selector(
        centralManagerDidUpdateState_,
        signature=b"v@:@",
        isRequired=True
    )
    
    # Add alternative method that might be called instead
    def centralManager_didUpdateState_(self, central, state):
        """Alternative method signature that might be called by the system."""
        print(f"DEBUG: centralManager_didUpdateState_ called with state: {state}")
        states = {
            CoreBluetooth.CBManagerStatePoweredOff: "Bluetooth is powered off",
            CoreBluetooth.CBManagerStatePoweredOn: "Bluetooth is powered on",
            CoreBluetooth.CBManagerStateResetting: "Bluetooth is resetting",
            CoreBluetooth.CBManagerStateUnauthorized: "Bluetooth is unauthorized",
            CoreBluetooth.CBManagerStateUnknown: "Bluetooth is unknown",
            CoreBluetooth.CBManagerStateUnsupported: "Bluetooth is not supported"
        }
        
        print(f"Bluetooth state: {states.get(state, 'Unknown')}")
        
        if state == CoreBluetooth.CBManagerStatePoweredOn:
            print("Bluetooth is ready, starting scan...")
            self.listener.start_scanning()
        else:
            print("Bluetooth is not ready for scanning")
            if state == CoreBluetooth.CBManagerStatePoweredOff:
                print("Please turn on Bluetooth in System Settings and try again.")
            elif state == CoreBluetooth.CBManagerStateUnauthorized:
                print("Please grant Bluetooth permission to this application.")

class LocationManagerDelegate(NSObject):
    """Delegate for handling Core Location manager events."""
    
    def initWithListener_(self, listener):
        self = objc.super(LocationManagerDelegate, self).init()
        if self is None:
            return None
        self.listener = listener
        return self
    
    def locationManager_didRangeBeacons_inRegion_(self, manager, beacons, region):
        if len(beacons) > 0:
            print(f"\nFound {len(beacons)} beacons in region {region.identifier()}:")
            for beacon in beacons:
                proximity_names = {
                    CoreLocation.CLProximityUnknown: "Unknown",
                    CoreLocation.CLProximityImmediate: "Immediate",
                    CoreLocation.CLProximityNear: "Near",
                    CoreLocation.CLProximityFar: "Far"
                }
                
                proximity = proximity_names.get(beacon.proximity(), "Unknown")
                
                print(f"  UUID: {beacon.proximityUUID().UUIDString()}")
                print(f"  Major: {beacon.major().intValue()}")
                print(f"  Minor: {beacon.minor().intValue()}")
                print(f"  RSSI: {beacon.rssi()} dBm")
                print(f"  Proximity: {proximity}")
                print(f"  Accuracy: {beacon.accuracy():.2f} meters")
                print("  ----------------------")
    
    def locationManager_didFailWithError_(self, manager, error):
        print(f"Location manager failed with error: {error}")
    
    def locationManager_didChangeAuthorizationStatus_(self, manager, status):
        auth_status = {
            CoreLocation.kCLAuthorizationStatusNotDetermined: "Not Determined",
            CoreLocation.kCLAuthorizationStatusRestricted: "Restricted",
            CoreLocation.kCLAuthorizationStatusDenied: "Denied",
            CoreLocation.kCLAuthorizationStatusAuthorizedAlways: "Authorized Always",
            CoreLocation.kCLAuthorizationStatusAuthorizedWhenInUse: "Authorized When In Use"
        }
        
        print(f"Location authorization status: {auth_status.get(status, 'Unknown')}")
        
        if status in [CoreLocation.kCLAuthorizationStatusAuthorizedWhenInUse, 
                     CoreLocation.kCLAuthorizationStatusAuthorizedAlways]:
            self.listener.start_monitoring()
    
    def locationManager_monitoringDidFailForRegion_withError_(self, manager, region, error):
        print(f"Monitoring failed for region {region.identifier()}: {error}")
    
    def locationManager_rangingBeaconsDidFailForRegion_withError_(self, manager, region, error):
        print(f"Ranging beacons failed for region {region.identifier()}: {error}")

class BeaconListener:
    """Main class for listening to iBeacon signals."""
    
    def __init__(self):
        print("Initializing Beacon Listener...")
        
        # Create Core Bluetooth central manager
        self.central_delegate = CentralManagerDelegate.alloc().initWithListener_(self)
        print("Central delegate created")
        
        # Force an immediate check of Bluetooth state
        self.central_manager = CoreBluetooth.CBCentralManager.alloc().initWithDelegate_queue_(
            self.central_delegate, None
        )
        print("Central manager created")
        
        # Print the current Bluetooth state
        state = self.central_manager.state()
        states = {
            CoreBluetooth.CBManagerStatePoweredOff: "Bluetooth is powered off",
            CoreBluetooth.CBManagerStatePoweredOn: "Bluetooth is powered on",
            CoreBluetooth.CBManagerStateResetting: "Bluetooth is resetting",
            CoreBluetooth.CBManagerStateUnauthorized: "Bluetooth is unauthorized",
            CoreBluetooth.CBManagerStateUnknown: "Bluetooth is unknown",
            CoreBluetooth.CBManagerStateUnsupported: "Bluetooth is not supported"
        }
        print(f"DEBUG: Initial Bluetooth state: {states.get(state, 'Unknown state code: ' + str(state))}")
        
        # If Bluetooth is already on, start scanning immediately
        if state == CoreBluetooth.CBManagerStatePoweredOn:
            print("Bluetooth is already on, starting scan immediately...")
            self.start_scanning()
        elif state == CoreBluetooth.CBManagerStateUnknown:
            print("Bluetooth state is initializing. Waiting for state update...")
            print("If this persists, please check if Bluetooth is enabled in System Settings.")
        elif state == CoreBluetooth.CBManagerStatePoweredOff:
            print("ERROR: Bluetooth is powered off. Please turn on Bluetooth in System Settings.")
        elif state == CoreBluetooth.CBManagerStateUnauthorized:
            print("ERROR: Bluetooth access is unauthorized. Please grant Bluetooth permission to this application.")
        
        # Create Core Location manager
        self.location_delegate = LocationManagerDelegate.alloc().initWithListener_(self)
        self.location_manager = CoreLocation.CLLocationManager.alloc().init()
        self.location_manager.setDelegate_(self.location_delegate)
        
        # Request location authorization
        auth_status = self.location_manager.authorizationStatus()
        if auth_status == CoreLocation.kCLAuthorizationStatusNotDetermined:
            print("Requesting location authorization...")
            self.location_manager.requestWhenInUseAuthorization()
        elif auth_status in [CoreLocation.kCLAuthorizationStatusAuthorizedWhenInUse, CoreLocation.kCLAuthorizationStatusAuthorizedAlways]:
            print("Location authorization already granted.")
        else:
            print("WARNING: Location services are not authorized. Please enable location services for this app in System Settings.")
        
        # Store monitored regions
        self.monitored_regions = []
        
        print("Beacon Listener initialized")
        if state != CoreBluetooth.CBManagerStatePoweredOn:
            print("Waiting for Bluetooth to be ready...")
    
    def start_scanning(self):
        """Start scanning for Bluetooth devices."""
        scan_options = {
            CoreBluetooth.CBCentralManagerScanOptionAllowDuplicatesKey: True
        }
        self.central_manager.scanForPeripheralsWithServices_options_(None, scan_options)
        print("Scanning for Bluetooth devices...")
    
    def start_monitoring(self):
        """Start monitoring for iBeacons."""
        print("Starting to monitor for iBeacons...")
        
        # Monitor for all iBeacons by using a wildcard UUID
        # Note: In a real application, you might want to monitor for specific UUIDs
        # Here we're using a common iBeacon UUID as an example
        uuid = NSUUID.alloc().initWithUUIDString_("E2C56DB5-DFFB-48D2-B060-D0F5A71096E0")
        region = CoreLocation.CLBeaconRegion.alloc().initWithUUID_identifier_(
            uuid, "WildcardRegion"
        )
        
        # Start monitoring and ranging
        self.location_manager.startMonitoringForRegion_(region)
        self.location_manager.startRangingBeaconsInRegion_(region)
        
        self.monitored_regions.append(region)
        print(f"Monitoring for iBeacons with UUID: {uuid.UUIDString()}")
        
        # Add more common iBeacon UUIDs
        common_uuids = [
            "F7826DA6-4FA2-4E98-8024-BC5B71E0893E",  # Kontakt.io
            "8AEFB031-6C32-486F-825B-E26FA193487D",  # Gimbal
            "B9407F30-F5F8-466E-AFF9-25556B57FE6D",  # Estimote
            "D0D3FA86-CA76-45EC-9BD9-6AF4FB75EB95",  # Radius Networks
            "A0B13730-3A9A-11E3-AA6E-0800200C9A66",  # Roximity
            "61687109-905F-4436-91F8-E602F514C96D",  # BlueCats
            "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0",  # Apple AirLocate
            "F0018B9B-7509-4C31-A905-1A27D39C003C",  # Aruba
            "00000000-0000-0000-0000-000000000000"   # Wildcard for any UUID
        ]
        
        for uuid_str in common_uuids:
            if uuid_str == "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0":
                continue  # Skip the one we already added
                
            uuid = NSUUID.alloc().initWithUUIDString_(uuid_str)
            region_id = f"Region-{uuid_str[:8]}"
            region = CoreLocation.CLBeaconRegion.alloc().initWithUUID_identifier_(
                uuid, region_id
            )
            
            self.location_manager.startMonitoringForRegion_(region)
            self.location_manager.startRangingBeaconsInRegion_(region)
            
            self.monitored_regions.append(region)
            print(f"Monitoring for iBeacons with UUID: {uuid_str}")
    
    def stop(self):
        """Stop monitoring and scanning."""
        # Stop ranging and monitoring for all regions
        for region in self.monitored_regions:
            self.location_manager.stopRangingBeaconsInRegion_(region)
            self.location_manager.stopMonitoringForRegion_(region)
        
        # Stop scanning for Bluetooth devices
        self.central_manager.stopScan()
        print("Stopped monitoring and scanning")

def main():
    print("Starting Beacon Listener...")
    print("This program will listen for any iBeacon signals.")
    print("Press Ctrl+C to exit.")
    
    try:
        listener = BeaconListener()
        
        # Keep the program running
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    except KeyboardInterrupt:
        print("\nStopping Beacon Listener...")
        if 'listener' in locals():
            listener.stop()
        print("Beacon Listener stopped.")

if __name__ == "__main__":
    main()
