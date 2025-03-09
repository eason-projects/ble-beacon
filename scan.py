import asyncio
from bleak import BleakScanner
import struct
import uuid

async def scan_ble_devices():
    devices_with_adv = await BleakScanner.discover(return_adv=True)
    for address, (device, advertisement_data) in devices_with_adv.items():
        if advertisement_data.manufacturer_data:
            for manufacturer_id, data in advertisement_data.manufacturer_data.items():
                print(f"-- Device Name: {device.name}, Address: {device.address}, RSSI: {advertisement_data.rssi}, Manufacturer ID: {manufacturer_id}, Data: {data.hex()}")

                if manufacturer_id == 76:  # Apple's manufacturer ID
                    if len(data) >= 23 and data[0] == 0x02 and data[1] == 0x15: #ibeacon prefix.
                        try:
                            beacon_uuid = uuid.UUID(bytes=bytes(data[2:18]))
                            major, minor = struct.unpack(">HH", data[18:22])
                            rssi = advertisement_data.rssi
                            print(f">> iBeacon - UUID: {beacon_uuid}, Major: {major}, Minor: {minor}, RSSI: {rssi}")
                        except ValueError:
                            print(f"Device Name: {device.name}, Address: {device.address}, RSSI: {advertisement_data.rssi}, but manufacturer data format is wrong")
                    else:
                        print(f"Device Name: {device.name}, Address: {device.address}, RSSI: {advertisement_data.rssi}, Manufacturer ID: {manufacturer_id}, Data: {data.hex()}")
                else:
                    print(f"Device Name: {device.name}, Address: {device.address}, RSSI: {advertisement_data.rssi}, Manufacturer ID: {manufacturer_id}, Data: {data.hex()}")
        else:
            print(f"Device Name: {device.name}, Address: {device.address}, RSSI: {advertisement_data.rssi}")

if __name__ == "__main__":
    asyncio.run(scan_ble_devices())