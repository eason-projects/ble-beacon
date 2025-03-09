import asyncio
from bleak import BleakScanner
import struct
import uuid
import time
import socket
import platform
import os
import uuid as system_uuid
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
import datetime

# Kafka configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'ble_beacons')

# Initialize Kafka producer
def create_kafka_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            api_version=(0, 10, 1)
        )
        print(f"Successfully connected to Kafka broker at {KAFKA_BROKER}")
        return producer
    except Exception as e:
        print(f"Error connecting to Kafka: {e}")
        return None

def get_host_id():
    host_id = None
    
    # Try to get a more persistent machine ID if available
    try:
        if platform.system() == "Linux":
            # Try to read machine-id on Linux
            if os.path.exists('/etc/machine-id'):
                with open('/etc/machine-id', 'r') as f:
                    host_id = f.read().strip()
        elif platform.system() == "Darwin":  # macOS
            # Try to get hardware UUID on macOS
            import subprocess
            result = subprocess.run(['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'], 
                                   capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if 'IOPlatformUUID' in line:
                    host_id = line.split('"')[-2]
                    break
    except Exception as e:
        print(f"Warning: Could not get persistent machine ID: {e}")
    
    return host_id

# Helper function to process and send beacon data to Kafka
def process_beacon_data(producer, beacon_type, beacon_data, host_id, timestamp):
    # Add common fields
    beacon_data.update({
        "type": beacon_type,
        "host_id": host_id,
        "timestamp": timestamp
    })
    
    # Print beacon information based on type
    if beacon_type == "iBeacon":
        print(f"iBeacon - UUID: {beacon_data['uuid']}, Major: {beacon_data['major']}, Minor: {beacon_data['minor']}, RSSI: {beacon_data['rssi']}, Address: {beacon_data['address']}, Name: {beacon_data['name']}")
    elif beacon_type.startswith("Eddystone"):
        print(f"{beacon_type} - Address: {beacon_data['address']}, RSSI: {beacon_data['rssi']}, Name: {beacon_data['name']}")
    elif beacon_type == "AltBeacon":
        print(f"AltBeacon - ID: {beacon_data['id']}, RSSI: {beacon_data['rssi']}, Address: {beacon_data['address']}, Name: {beacon_data['name']}")
    
    # Send to Kafka if producer is available
    if producer:
        producer.send(KAFKA_TOPIC, beacon_data)
    
    return 1  # Return 1 to increment beacon count

# Create a beacon processor function that captures host_id and producer
def create_beacon_processor(host_id, producer):
    def process_beacon(beacon_type, beacon_data):
        timestamp = datetime.datetime.now().isoformat()
        return process_beacon_data(producer, beacon_type, beacon_data, host_id, timestamp)
    return process_beacon

async def scan_ble_devices():
    try:
        # Get host identification information
        host_id = get_host_id()
        print(f"Host ID: {host_id}")
        
        # Initialize Kafka producer
        producer = create_kafka_producer()
        if not producer:
            print("Warning: Kafka producer not available. Data will only be printed to console.")
        
        # Create a beacon processor that captures host_id and producer
        process_beacon = create_beacon_processor(host_id, producer)
        
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
                                
                                beacon_data = {
                                    "uuid": str(beacon_uuid),
                                    "major": major,
                                    "minor": minor,
                                    "rssi": advertisement_data.rssi,
                                    "address": device.address,
                                    "name": device.name or "Unknown"
                                }
                                
                                beacon_count += process_beacon("iBeacon", beacon_data)
                            except ValueError:
                                pass  # Skip malformed iBeacon data
                        
                        # Check for Eddystone beacons (Google)
                        elif manufacturer_id == 0x00E0 or (manufacturer_id == 0x0499 and len(data) >= 14):  # Google's manufacturer ID or potential Eddystone
                            # Simple check for Eddystone frame
                            if len(advertisement_data.service_data) > 0 and "0000feaa-0000-1000-8000-00805f9b34fb" in advertisement_data.service_data:
                                eddystone_data = advertisement_data.service_data["0000feaa-0000-1000-8000-00805f9b34fb"]
                                frame_type = eddystone_data[0] if len(eddystone_data) > 0 else None
                                
                                beacon_data = {
                                    "address": device.address,
                                    "rssi": advertisement_data.rssi,
                                    "name": device.name or "Unknown"
                                }
                                
                                if frame_type == 0x00:  # UID frame
                                    beacon_count += process_beacon("Eddystone-UID", beacon_data)
                                elif frame_type == 0x10:  # URL frame
                                    beacon_count += process_beacon("Eddystone-URL", beacon_data)
                                elif frame_type == 0x20:  # TLM frame
                                    beacon_count += process_beacon("Eddystone-TLM", beacon_data)
                        
                        # Check for AltBeacon (Radius Networks)
                        elif len(data) >= 24 and data[0] == 0xBE and data[1] == 0xAC:  # AltBeacon prefix
                            try:
                                beacon_id = data[2:22].hex()
                                
                                beacon_data = {
                                    "id": beacon_id,
                                    "rssi": advertisement_data.rssi,
                                    "address": device.address,
                                    "name": device.name or "Unknown"
                                }
                                
                                beacon_count += process_beacon("AltBeacon", beacon_data)
                            except Exception:
                                pass  # Skip malformed AltBeacon data
            
            if beacon_count == 0:
                print("No beacons found during this scan.")
            else:
                print(f"Found {beacon_count} beacons in this scan.")
                # Flush Kafka messages to ensure they're sent
                if producer:
                    producer.flush()
            
            # Continue immediately to the next scan without waiting
            print("Starting next scan immediately...")
            
    except KeyboardInterrupt:
        print("\nScanning stopped by user.")
        if 'producer' in locals() and producer:
            producer.flush()
            producer.close()
            print("Kafka producer closed.")
    except Exception as e:
        print(f"\nError during scanning: {e}")
        if 'producer' in locals() and producer:
            producer.close()

if __name__ == "__main__":
    asyncio.run(scan_ble_devices())