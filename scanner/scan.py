import asyncio
from bleak import BleakScanner
import struct
import uuid
import time

async def scan_ble_devices():
    try:
        print("Starting continuous BLE beacon scanner. Press Ctrl+C to stop.")
        scan_count = 0
        
        while True:
            scan_count += 1
            print(f"\n--- Scan #{scan_count} ---")
            print("Scanning for BLE beacons...")
            
            devices_with_adv = await BleakScanner.discover(
                timeout=1.0,
                return_adv=True,
            )
            
            beacon_count = 0
            for address, (device, advertisement_data) in devices_with_adv.items():
                if advertisement_data.manufacturer_data:
                    for manufacturer_id, data in advertisement_data.manufacturer_data.items():
                        # Check for iBeacon (Apple)
                        if manufacturer_id == 76 and len(data) >= 23 and data[0] == 0x02 and data[1] == 0x15:
                            try:
                                beacon_uuid = uuid.UUID(bytes=bytes(data[2:18]))
                                major, minor = struct.unpack(">HH", data[18:22])
                                rssi = advertisement_data.rssi
                                print(f"iBeacon - UUID: {beacon_uuid}, Major: {major}, Minor: {minor}, RSSI: {rssi}, Address: {device.address}, Name: {device.name or 'Unknown'}")
                                beacon_count += 1
                            except ValueError:
                                pass  # Skip malformed iBeacon data
                        
                        # Check for Eddystone beacons (Google)
                        elif manufacturer_id == 0x00E0 or (manufacturer_id == 0x0499 and len(data) >= 14):  # Google's manufacturer ID or potential Eddystone
                            # Simple check for Eddystone frame
                            if len(advertisement_data.service_data) > 0 and "0000feaa-0000-1000-8000-00805f9b34fb" in advertisement_data.service_data:
                                eddystone_data = advertisement_data.service_data["0000feaa-0000-1000-8000-00805f9b34fb"]
                                frame_type = eddystone_data[0] if len(eddystone_data) > 0 else None
                                
                                if frame_type == 0x00:  # UID frame
                                    print(f"Eddystone-UID - Address: {device.address}, RSSI: {advertisement_data.rssi}, Name: {device.name or 'Unknown'}")
                                    beacon_count += 1
                                elif frame_type == 0x10:  # URL frame
                                    print(f"Eddystone-URL - Address: {device.address}, RSSI: {advertisement_data.rssi}, Name: {device.name or 'Unknown'}")
                                    beacon_count += 1
                                elif frame_type == 0x20:  # TLM frame
                                    print(f"Eddystone-TLM - Address: {device.address}, RSSI: {advertisement_data.rssi}, Name: {device.name or 'Unknown'}")
                                    beacon_count += 1
                        
                        # Check for AltBeacon (Radius Networks)
                        elif len(data) >= 24 and data[0] == 0xBE and data[1] == 0xAC:  # AltBeacon prefix
                            try:
                                beacon_id = data[2:22].hex()
                                rssi = advertisement_data.rssi
                                print(f"AltBeacon - ID: {beacon_id}, RSSI: {rssi}, Address: {device.address}, Name: {device.name or 'Unknown'}")
                                beacon_count += 1
                            except Exception:
                                pass  # Skip malformed AltBeacon data
            
            if beacon_count == 0:
                print("No beacons found during this scan.")
            else:
                print(f"Found {beacon_count} beacons in this scan.")
            
            # Continue immediately to the next scan without waiting
            print("Starting next scan immediately...")
            
    except KeyboardInterrupt:
        print("\nScanning stopped by user.")
    except Exception as e:
        print(f"\nError during scanning: {e}")

if __name__ == "__main__":
    asyncio.run(scan_ble_devices())