import asyncio
import time
import mlflow
from bleak import BleakScanner, BleakClient
import math
import json
import os
import yaml
from collections import defaultdict

# Set MLflow tracking URI
mlflow.set_tracking_uri("http://localhost:8090")
mlflow.set_experiment("ble_scanning")

# 设备类型特征库 - 根据广告数据特征识别设备类型
DEVICE_SIGNATURES = {
    # 某些已知的服务UUID与设备类型的对应关系
    "0000180f-0000-1000-8000-00805f9b34fb": "电池服务",
    "0000180a-0000-1000-8000-00805f9b34fb": "设备信息服务",
    "0000fe9f-0000-1000-8000-00805f9b34fb": "苹果设备",
    "0000fd6f-0000-1000-8000-00805f9b34fb": "谷歌Fast Pair",
    "0000fdaa-0000-1000-8000-00805f9b34fb": "小米生态链设备",
    # 添加更多已知的服务UUID
}

# 初始化制造商ID映射
MANUFACTURER_IDS = {
    76: "Apple, Inc.",
    6: "Microsoft",
    117: "Samsung Electronics Co. Ltd.",
    224: "Google Inc.",
    911: "小米/Xiaomi",
    424: "AIMA Technology",
    # 添加更多已知的制造商ID
}

# 从YAML文件加载制造商ID
def load_company_identifiers():
    """从YAML文件加载蓝牙SIG分配的公司标识符"""
    try:
        if os.path.exists("company_identifiers.yaml"):
            with open("company_identifiers.yaml", 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                if data and 'company_identifiers' in data:
                    # 创建映射字典: {ID值(十进制): 公司名称}
                    company_map = {}
                    for company in data['company_identifiers']:
                        # 将十六进制值转换为十进制
                        if 'value' in company and 'name' in company:
                            try:
                                # 处理不同格式的十六进制值
                                if isinstance(company['value'], str):
                                    decimal_value = int(company['value'], 16)
                                else:
                                    decimal_value = company['value']
                                company_map[decimal_value] = company['name']
                            except (ValueError, TypeError) as e:
                                print(f"解析公司ID出错: {e}, 值: {company['value']}")
                    return company_map
            print("未找到有效的公司标识符数据")
        else:
            print("未找到company_identifiers.yaml文件")
    except Exception as e:
        print(f"加载公司标识符文件出错: {e}")
    return {}

# 保存设备映射表的文件
DEVICES_FILE = "known_devices.json"

# 已知设备映射表 - 可以根据实际情况修改
KNOWN_DEVICES = {
    # 格式: "MAC地址": {"name": "设备名称", "type": "设备类型", "location": "位置描述"}
    # 例如:
    # "AA:BB:CC:DD:EE:FF": {"name": "我的iPhone", "type": "手机", "location": "随身携带"},
    # "11:22:33:44:55:66": {"name": "客厅灯", "type": "智能灯", "location": "客厅"},
}

# 设备识别次数统计
DEVICE_DETECTION_COUNT = defaultdict(int)

# 加载制造商ID映射
try:
    company_map = load_company_identifiers()
    if company_map:
        print(f"成功加载 {len(company_map)} 个公司标识符")
        # 更新MANUFACTURER_IDS，但保留我们自定义的映射
        for id_value, name in company_map.items():
            if id_value not in MANUFACTURER_IDS:
                MANUFACTURER_IDS[id_value] = name
    else:
        print("未能加载公司标识符，将使用默认映射")
except Exception as e:
    print(f"初始化公司标识符时出错: {e}")

def load_known_devices():
    """从文件加载已知设备映射表"""
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载设备文件出错: {e}")
    return {}

def save_known_devices(devices):
    """保存已知设备映射表到文件"""
    try:
        with open(DEVICES_FILE, 'w') as f:
            json.dump(devices, f, indent=2)
    except Exception as e:
        print(f"保存设备文件出错: {e}")

def save_detection_counts():
    """保存设备识别次数到文件"""
    try:
        with open("device_detection_counts.json", 'w') as f:
            # 将defaultdict转换为普通dict以便JSON序列化
            json.dump(dict(DEVICE_DETECTION_COUNT), f, indent=2)
    except Exception as e:
        print(f"保存设备识别次数文件出错: {e}")

def load_detection_counts():
    """从文件加载设备识别次数"""
    if os.path.exists("device_detection_counts.json"):
        try:
            with open("device_detection_counts.json", 'r') as f:
                counts = json.load(f)
                # 将普通dict转换为defaultdict
                result = defaultdict(int)
                for k, v in counts.items():
                    result[k] = v
                return result
        except Exception as e:
            print(f"加载设备识别次数文件出错: {e}")
    return defaultdict(int)

def estimate_distance(rssi, tx_power=-59):
    """
    根据RSSI估算距离（米）
    tx_power是在1米距离测得的RSSI值，默认使用-59dBm
    """
    if rssi == 0:
        return -1.0  # 无法计算
    
    # 使用对数距离路径损耗模型
    ratio = rssi * 1.0 / tx_power
    if ratio < 1.0:
        return pow(ratio, 10)
    else:
        return 0.89976 * pow(ratio, 7.7095) + 0.111

def identify_device_type(advertisement_data):
    """根据广告数据识别设备类型"""
    device_type = "未知设备"
    
    # 检查服务UUID
    if advertisement_data.service_uuids:
        for uuid in advertisement_data.service_uuids:
            if uuid.lower() in DEVICE_SIGNATURES:
                return DEVICE_SIGNATURES[uuid.lower()]
    
    # 检查制造商数据
    if advertisement_data.manufacturer_data:
        # 苹果设备通常使用制造商ID 0x004C
        if 76 in advertisement_data.manufacturer_data:  # 0x004C = 76
            return "苹果设备"
        # 其他制造商ID判断...
    
    return device_type

def parse_manufacturer_data(manufacturer_id, data):
    """
    解析制造商数据
    
    Args:
        manufacturer_id: 制造商ID
        data: 二进制数据
    
    Returns:
        解析后的信息字典
    """
    result = {
        "manufacturer": MANUFACTURER_IDS.get(manufacturer_id, f"未知制造商 (ID: {manufacturer_id}, 十六进制: 0x{manufacturer_id:04X})"),
        "raw_data": data.hex(),
        "parsed": {}
    }
    
    try:
        # 苹果设备 (iBeacon)
        if manufacturer_id == 76 and len(data) >= 25 and data[0:2] == b'\x02\x15':
            # iBeacon格式
            uuid = '-'.join([
                data[2:6].hex(),
                data[6:8].hex(),
                data[8:10].hex(),
                data[10:12].hex(),
                data[12:18].hex()
            ]).upper()
            major = int.from_bytes(data[18:20], byteorder='big')
            minor = int.from_bytes(data[20:22], byteorder='big')
            tx_power = data[22] - 256 if data[22] > 127 else data[22]
            
            result["parsed"] = {
                "type": "iBeacon",
                "uuid": uuid,
                "major": major,
                "minor": minor,
                "tx_power": tx_power
            }
        
        # 小米设备
        elif manufacturer_id == 911:
            result["parsed"] = {
                "type": "小米设备",
                "可能用途": "设备识别、状态信息或配对数据"
            }
            
            # 尝试提取小米设备的一些常见信息
            if len(data) > 5:
                # 一些小米设备在数据开头有特定标识
                result["parsed"]["数据标识"] = data[0:2].hex()
        
        # AIMA设备
        elif manufacturer_id == 424:
            result["parsed"] = {
                "type": "AIMA设备",
                "可能用途": "设备状态、识别码或配对信息"
            }
        
        # 谷歌Fast Pair
        elif manufacturer_id == 224 and len(data) >= 3 and data[0] == 0x00:
            model_id = int.from_bytes(data[1:3], byteorder='big')
            result["parsed"] = {
                "type": "Google Fast Pair",
                "model_id": model_id
            }
            
    except Exception as e:
        result["error"] = str(e)
    
    return result

async def scan_ble_devices():
    # 加载已知设备映射表和识别次数
    global KNOWN_DEVICES, DEVICE_DETECTION_COUNT
    KNOWN_DEVICES.update(load_known_devices())
    DEVICE_DETECTION_COUNT.update(load_detection_counts())
    
    # Start an MLflow run
    with mlflow.start_run(run_name="ble_scanning"):
        print("Starting BLE scanning and logging to MLflow...")
        print(f"MLflow tracking URI: {mlflow.get_tracking_uri()}")
        print(f"MLflow experiment ID: {mlflow.active_run().info.experiment_id}")
        print(f"MLflow run ID: {mlflow.active_run().info.run_id}")
        
        # 创建一个设备缓存，避免重复记录参数
        known_devices = set()
        
        try:
            # Continuous scanning loop
            while True:
                print("=" * 50)
                # 使用更短的扫描时间和更多的扫描选项
                devices_with_adv = await BleakScanner.discover(
                    timeout=3.0,  # 减少单次扫描时间
                    return_adv=True,
                    scanning_mode="active"  # 使用主动扫描模式获取更多信息
                )
                timestamp = time.time()
                
                # 用于按制造商分组的数据结构
                manufacturers_devices = defaultdict(list)
                # 用于存储制造商ID的映射
                manufacturer_id_map = {}
                
                # 创建处理任务列表
                processing_tasks = []
                
                for address, (device, advertisement_data) in devices_with_adv.items():
                    # 更新设备识别次数
                    DEVICE_DETECTION_COUNT[address] += 1
                    
                    # 创建异步任务处理每个设备
                    task = asyncio.create_task(
                        process_device(address, device, advertisement_data, timestamp, known_devices, manufacturers_devices, manufacturer_id_map)
                    )
                    processing_tasks.append(task)
                
                # 等待所有处理任务完成
                if processing_tasks:
                    await asyncio.gather(*processing_tasks)
                
                # 显示按制造商分组的统计信息
                print("\n" + "=" * 20 + " 制造商设备统计 " + "=" * 20)
                print(f"本次扫描共发现 {len(devices_with_adv)} 个设备，涉及 {len(manufacturers_devices)} 个制造商")
                
                # 按制造商ID排序
                sorted_manufacturers = []
                for manufacturer_name, devices in manufacturers_devices.items():
                    # 获取制造商ID，如果不存在则使用最大值作为默认值
                    manufacturer_id = manufacturer_id_map.get(manufacturer_name, 0xFFFF)
                    sorted_manufacturers.append((manufacturer_name, devices, manufacturer_id))
                
                # 按ID排序
                sorted_manufacturers.sort(key=lambda x: x[2])
                
                for manufacturer_name, devices, manufacturer_id in sorted_manufacturers:
                    device_types = {}
                    for device_info in devices:
                        device_type = device_info["type"]
                        if device_type in device_types:
                            device_types[device_type] += 1
                        else:
                            device_types[device_type] = 1
                    
                    # 显示制造商及其设备类型统计
                    id_display = f"0x{manufacturer_id:04X}" if manufacturer_id != 0xFFFF else "未知"
                    print(f"\n制造商: {manufacturer_name} (ID: {id_display}) - 共 {len(devices)} 个设备")
                    print("设备类型统计:")
                    for device_type, count in device_types.items():
                        print(f"  - {device_type}: {count} 个")
                    
                    # 显示该制造商的设备列表
                    print("设备列表:")
                    # 按信号强度排序设备（信号越强排越前面）
                    sorted_devices = sorted(devices, key=lambda x: x["rssi"], reverse=True)
                    for device_info in sorted_devices:
                        address = device_info["address"]
                        detection_count = DEVICE_DETECTION_COUNT[address]
                        print(f"  - {device_info['name']} (地址: {address}, RSSI: {device_info['rssi']}, "
                              f"距离: {device_info['distance']:.2f}米, 识别次数: {detection_count}次)")
                
                print("=" * 60 + "\n")
                
                # 每10次扫描保存一次识别次数
                if sum(1 for count in DEVICE_DETECTION_COUNT.values() if count % 10 == 0) > 0:
                    save_detection_counts()
                
                # 减少扫描间隔时间
                await asyncio.sleep(0.01)  # 从5秒减少到1秒
                
        except KeyboardInterrupt:
            print("Scanning stopped by user")
            # 保存设备映射表和识别次数
            save_known_devices(KNOWN_DEVICES)
            save_detection_counts()
        except Exception as e:
            print(f"Error during scanning: {e}")
        finally:
            print("Scanning complete")
            # 保存设备映射表和识别次数
            save_known_devices(KNOWN_DEVICES)
            save_detection_counts()

async def process_device(address, device, advertisement_data, timestamp, known_devices, manufacturers_devices=None, manufacturer_id_map=None):
    """异步处理单个设备的数据"""
    device_name = device.name or "Unknown"
    rssi = advertisement_data.rssi
    
    # 估算距离
    distance = estimate_distance(rssi)
    
    # 识别设备类型
    device_type = identify_device_type(advertisement_data)
    
    # 检查是否是已知设备
    device_info = "未知设备"
    if address in KNOWN_DEVICES:
        device_info = f"{KNOWN_DEVICES[address]['name']} ({KNOWN_DEVICES[address]['type']}, {KNOWN_DEVICES[address]['location']})"
    else:
        # 如果是新设备且有名称，添加到已知设备列表
        if device_name != "Unknown":
            KNOWN_DEVICES[address] = {
                "name": device_name,
                "type": device_type,
                "location": f"首次发现于 {time.strftime('%Y-%m-%d %H:%M:%S')}"
            }
    
    # 获取设备识别次数
    detection_count = DEVICE_DETECTION_COUNT[address]
    
    # 打印详细信息
    print(f"设备: {device_name}, 地址: {address}, RSSI: {rssi}, 估计距离: {distance:.2f}米, 识别次数: {detection_count}次")
    print(f"设备类型: {device_type}")
    if address in KNOWN_DEVICES:
        print(f"已知设备: {device_info}")
    
    # 打印广告数据详情
    print(f"服务UUID: {advertisement_data.service_uuids}")
    
    # 制造商信息
    manufacturer_name = "未知制造商"
    
    if advertisement_data.manufacturer_data:
        print(f"制造商数据: {advertisement_data.manufacturer_data}")
        
        # 解析制造商数据
        for manufacturer_id, data in advertisement_data.manufacturer_data.items():
            parsed_data = parse_manufacturer_data(manufacturer_id, data)
            manufacturer_name = parsed_data['manufacturer']
            print(f"制造商: {manufacturer_name} (ID: 0x{manufacturer_id:04X})")
            print(f"原始数据: {parsed_data['raw_data']}")
            
            if parsed_data.get("parsed"):
                print("解析结果:")
                for key, value in parsed_data["parsed"].items():
                    print(f"  {key}: {value}")
            
            if parsed_data.get("error"):
                print(f"解析错误: {parsed_data['error']}")
            
            # 如果提供了manufacturers_devices字典，添加设备信息
            if manufacturers_devices is not None:
                manufacturers_devices[manufacturer_name].append({
                    "name": device_name,
                    "address": address,
                    "rssi": rssi,
                    "distance": distance,
                    "type": device_type,
                    "detection_count": detection_count
                })
                
                # 记录制造商ID
                if manufacturer_id_map is not None:
                    manufacturer_id_map[manufacturer_name] = manufacturer_id
    
    print("-" * 50)
    
    # Log to MLflow
    mlflow.log_metrics({
        f"rssi_{address.replace(':', '_')}": rssi,
        f"distance_{address.replace(':', '_')}": distance,
        f"detection_count_{address.replace(':', '_')}": detection_count
    }, step=int(timestamp))
    
    # 只有首次发现设备时才记录参数
    if address not in known_devices:
        mlflow.log_param(f"device_{address.replace(':', '_')}_name", device_name)
        mlflow.log_param(f"device_{address.replace(':', '_')}_type", device_type)
        mlflow.log_param(f"device_{address.replace(':', '_')}_manufacturer", manufacturer_name)
        mlflow.log_param(f"device_{address.replace(':', '_')}_first_seen", time.strftime('%Y-%m-%d %H:%M:%S'))
        known_devices.add(address)

async def connect_and_get_info(address):
    """连接到设备并获取更多信息"""
    try:
        async with BleakClient(address) as client:
            if client.is_connected:
                print(f"已连接到设备 {address}")
                
                # 获取设备服务
                services = await client.get_services()
                for service in services:
                    print(f"服务: {service.uuid}")
                    for char in service.characteristics:
                        print(f"  特征: {char.uuid}, 属性: {char.properties}")
                        
                        # 尝试读取可读特征
                        if "read" in char.properties:
                            try:
                                value = await client.read_gatt_char(char.uuid)
                                print(f"    值: {value}")
                            except Exception as e:
                                print(f"    读取失败: {e}")
    except Exception as e:
        print(f"连接设备 {address} 失败: {e}")

if __name__ == "__main__":
    asyncio.run(scan_ble_devices())