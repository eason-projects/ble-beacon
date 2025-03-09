package com.example.blluetoothbeacon

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.bluetooth.le.AdvertiseCallback
import android.bluetooth.le.AdvertiseData
import android.bluetooth.le.AdvertiseSettings
import android.bluetooth.le.BluetoothLeAdvertiser
import android.content.Context
import android.os.ParcelUuid
import android.util.Log
import java.nio.ByteBuffer
import java.util.UUID

class BeaconService(private val context: Context) {
    
    companion object {
        private const val TAG = "BeaconService"
        // Default iBeacon UUID - you can customize this
        private val BEACON_UUID = UUID.fromString("E2C56DB5-DFFB-48D2-B060-D0F5A71096E0")
        // Default values for major and minor - you can customize these
        private const val MAJOR = 1
        private const val MINOR = 100
        // Default transmit power - you can adjust this for different range testing
        private const val TX_POWER = -59
        // Manufacturer ID for Apple (used in iBeacon format)
        private const val MANUFACTURER_ID = 0x004C
        // iBeacon prefix
        private val IBEACON_PREFIX = byteArrayOf(0x02, 0x15)
        // Default service UUID for identification
        private val SERVICE_UUID = UUID.fromString("0000FFFF-0000-1000-8000-00805F9B34FB")
        // Default device name
        private const val DEFAULT_DEVICE_NAME = "BLE-Beacon"
        
        // Transmission power levels
        const val POWER_ULTRA_LOW = AdvertiseSettings.ADVERTISE_TX_POWER_ULTRA_LOW
        const val POWER_LOW = AdvertiseSettings.ADVERTISE_TX_POWER_LOW
        const val POWER_MEDIUM = AdvertiseSettings.ADVERTISE_TX_POWER_MEDIUM
        const val POWER_HIGH = AdvertiseSettings.ADVERTISE_TX_POWER_HIGH
        
        // Advertising modes
        const val MODE_LOW_POWER = AdvertiseSettings.ADVERTISE_MODE_LOW_POWER
        const val MODE_BALANCED = AdvertiseSettings.ADVERTISE_MODE_BALANCED
        const val MODE_LOW_LATENCY = AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY
        
        // Error codes
        const val ADVERTISE_FAILED_DATA_TOO_LARGE = 1
        const val ADVERTISE_FAILED_TOO_MANY_ADVERTISERS = 2
        const val ADVERTISE_FAILED_ALREADY_STARTED = 3
        const val ADVERTISE_FAILED_INTERNAL_ERROR = 4
        const val ADVERTISE_FAILED_FEATURE_UNSUPPORTED = 5
    }
    
    private var bluetoothAdapter: BluetoothAdapter? = null
    private var bluetoothLeAdvertiser: BluetoothLeAdvertiser? = null
    private var isAdvertising = false
    private var onAdvertisingFailureListener: ((Int, String) -> Unit)? = null
    private var onAdvertisingSuccessListener: (() -> Unit)? = null
    
    init {
        val bluetoothManager = context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothAdapter = bluetoothManager.adapter
        bluetoothLeAdvertiser = bluetoothAdapter?.bluetoothLeAdvertiser
    }
    
    /**
     * Set listeners for advertising success and failure
     */
    fun setAdvertisingListeners(
        onSuccess: () -> Unit,
        onFailure: (Int, String) -> Unit
    ) {
        onAdvertisingSuccessListener = onSuccess
        onAdvertisingFailureListener = onFailure
    }
    
    /**
     * Start advertising as an iBeacon with standard parameters
     */
    fun startAdvertising(uuid: UUID = BEACON_UUID, major: Int = MAJOR, minor: Int = MINOR, txPower: Int = TX_POWER) {
        startAdvertisingWithOptions(uuid, major, minor, txPower, false, null, null)
    }
    
    /**
     * Start advertising with additional options for better identification
     * @param uuid The UUID for the iBeacon
     * @param major The major value for the iBeacon
     * @param minor The minor value for the iBeacon
     * @param txPower The TX power value for the iBeacon
     * @param includeDeviceName Whether to include the device name in the advertisement
     * @param customDeviceName Custom device name to use (if null, uses the device's name or DEFAULT_DEVICE_NAME)
     * @param customServiceUuid Custom service UUID to include in the advertisement (if null, uses SERVICE_UUID)
     * @param powerLevel The transmission power level (use POWER_* constants)
     * @param advertiseMode The advertising mode (use MODE_* constants)
     */
    fun startAdvertisingWithOptions(
        uuid: UUID = BEACON_UUID, 
        major: Int = MAJOR, 
        minor: Int = MINOR, 
        txPower: Int = TX_POWER,
        includeDeviceName: Boolean = false,
        customDeviceName: String? = null,
        customServiceUuid: UUID? = null,
        powerLevel: Int = POWER_HIGH,
        advertiseMode: Int = MODE_LOW_LATENCY
    ) {
        if (bluetoothAdapter == null || !bluetoothAdapter!!.isEnabled) {
            Log.e(TAG, "Bluetooth is not enabled")
            onAdvertisingFailureListener?.invoke(-1, "Bluetooth is not enabled")
            return
        }
        
        if (bluetoothLeAdvertiser == null) {
            Log.e(TAG, "BluetoothLeAdvertiser is not available")
            onAdvertisingFailureListener?.invoke(-1, "BluetoothLeAdvertiser is not available")
            return
        }
        
        if (isAdvertising) {
            Log.d(TAG, "Already advertising")
            return
        }
        
        // Set device name if provided
        if (customDeviceName != null) {
            bluetoothAdapter?.name = customDeviceName
            Log.d(TAG, "Set device name to: $customDeviceName")
        }
        
        // Create iBeacon advertisement data
        val manufacturerData = createiBeaconManufacturerData(uuid, major, minor, txPower)
        
        val advertiseSettings = AdvertiseSettings.Builder()
            .setAdvertiseMode(advertiseMode)
            .setTxPowerLevel(powerLevel)
            .setConnectable(false)
            .build()
            
        val advertiseDataBuilder = AdvertiseData.Builder()
            .setIncludeDeviceName(includeDeviceName)
            .setIncludeTxPowerLevel(false)
            .addManufacturerData(MANUFACTURER_ID, manufacturerData)
        
        // Add service UUID if provided
        if (customServiceUuid != null) {
            advertiseDataBuilder.addServiceUuid(ParcelUuid(customServiceUuid))
            Log.d(TAG, "Added custom service UUID: $customServiceUuid")
        }
        
        val advertiseData = advertiseDataBuilder.build()
        
        // Create scan response data with service UUID if not already in advertise data
        val scanResponseBuilder = AdvertiseData.Builder()
            .setIncludeTxPowerLevel(true)
        
        if (customServiceUuid == null) {
            scanResponseBuilder.addServiceUuid(ParcelUuid(SERVICE_UUID))
            Log.d(TAG, "Added default service UUID to scan response: $SERVICE_UUID")
        }
        
        val scanResponse = scanResponseBuilder.build()
            
        try {
            bluetoothLeAdvertiser?.startAdvertising(
                advertiseSettings, 
                advertiseData,
                scanResponse,
                advertiseCallback
            )
            Log.d(TAG, "Started advertising with UUID: $uuid, Major: $major, Minor: $minor, " +
                  "Include Name: $includeDeviceName, Power Level: $powerLevel, Mode: $advertiseMode")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start advertising: ${e.message}")
            onAdvertisingFailureListener?.invoke(-1, "Exception: ${e.message}")
        }
    }
    
    /**
     * Start advertising with simplified options for devices with limitations
     * This method reduces the payload size to avoid ADVERTISE_FAILED_DATA_TOO_LARGE errors
     */
    fun startSimplifiedAdvertising(
        uuid: UUID = BEACON_UUID,
        major: Int = MAJOR,
        minor: Int = MINOR,
        txPower: Int = TX_POWER,
        powerLevel: Int = POWER_HIGH,
        advertiseMode: Int = MODE_LOW_LATENCY
    ) {
        if (bluetoothAdapter == null || !bluetoothAdapter!!.isEnabled) {
            Log.e(TAG, "Bluetooth is not enabled")
            onAdvertisingFailureListener?.invoke(-1, "Bluetooth is not enabled")
            return
        }
        
        if (bluetoothLeAdvertiser == null) {
            Log.e(TAG, "BluetoothLeAdvertiser is not available")
            onAdvertisingFailureListener?.invoke(-1, "BluetoothLeAdvertiser is not available")
            return
        }
        
        if (isAdvertising) {
            Log.d(TAG, "Already advertising")
            return
        }
        
        // Create iBeacon advertisement data
        val manufacturerData = createiBeaconManufacturerData(uuid, major, minor, txPower)
        
        val advertiseSettings = AdvertiseSettings.Builder()
            .setAdvertiseMode(advertiseMode)
            .setTxPowerLevel(powerLevel)
            .setConnectable(false)
            .build()
            
        val advertiseData = AdvertiseData.Builder()
            .setIncludeDeviceName(false)
            .setIncludeTxPowerLevel(false)
            .addManufacturerData(MANUFACTURER_ID, manufacturerData)
            .build()
            
        try {
            bluetoothLeAdvertiser?.startAdvertising(
                advertiseSettings, 
                advertiseData,
                advertiseCallback
            )
            Log.d(TAG, "Started simplified advertising with UUID: $uuid, Major: $major, Minor: $minor, " +
                  "Power Level: $powerLevel, Mode: $advertiseMode")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start simplified advertising: ${e.message}")
            onAdvertisingFailureListener?.invoke(-1, "Exception: ${e.message}")
        }
    }
    
    /**
     * Get a human-readable description of the power level
     */
    fun getPowerLevelDescription(powerLevel: Int): String {
        return when (powerLevel) {
            POWER_ULTRA_LOW -> "Ultra Low (-21 dBm)"
            POWER_LOW -> "Low (-15 dBm)"
            POWER_MEDIUM -> "Medium (-7 dBm)"
            POWER_HIGH -> "High (0 dBm)"
            else -> "Unknown"
        }
    }
    
    /**
     * Get a human-readable description of the advertising mode
     */
    fun getAdvertiseModeDescription(mode: Int): String {
        return when (mode) {
            MODE_LOW_POWER -> "Low Power (1000ms)"
            MODE_BALANCED -> "Balanced (250ms)"
            MODE_LOW_LATENCY -> "Low Latency (100ms)"
            else -> "Unknown"
        }
    }
    
    /**
     * Get a human-readable description of an error code
     */
    fun getErrorDescription(errorCode: Int): String {
        return when (errorCode) {
            ADVERTISE_FAILED_DATA_TOO_LARGE -> "Data too large (try simplified mode)"
            ADVERTISE_FAILED_TOO_MANY_ADVERTISERS -> "Too many advertisers"
            ADVERTISE_FAILED_ALREADY_STARTED -> "Advertising already started"
            ADVERTISE_FAILED_INTERNAL_ERROR -> "Internal error"
            ADVERTISE_FAILED_FEATURE_UNSUPPORTED -> "Feature unsupported"
            else -> "Unknown error ($errorCode)"
        }
    }
    
    fun stopAdvertising() {
        if (!isAdvertising) {
            return
        }
        
        try {
            bluetoothLeAdvertiser?.stopAdvertising(advertiseCallback)
            isAdvertising = false
            Log.d(TAG, "Stopped advertising")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to stop advertising: ${e.message}")
        }
    }
    
    private val advertiseCallback = object : AdvertiseCallback() {
        override fun onStartSuccess(settingsInEffect: AdvertiseSettings) {
            super.onStartSuccess(settingsInEffect)
            isAdvertising = true
            Log.d(TAG, "Advertising started successfully")
            onAdvertisingSuccessListener?.invoke()
        }
        
        override fun onStartFailure(errorCode: Int) {
            super.onStartFailure(errorCode)
            isAdvertising = false
            val errorMessage = getErrorDescription(errorCode)
            Log.e(TAG, "Advertising failed to start with error code: $errorCode ($errorMessage)")
            onAdvertisingFailureListener?.invoke(errorCode, errorMessage)
        }
    }
    
    private fun createiBeaconManufacturerData(uuid: UUID, major: Int, minor: Int, txPower: Int): ByteArray {
        val uuidBytes = getBytesFromUUID(uuid)
        val majorBytes = shortToByteArray(major.toShort())
        val minorBytes = shortToByteArray(minor.toShort())
        
        val manufacturerData = ByteArray(IBEACON_PREFIX.size + uuidBytes.size + majorBytes.size + minorBytes.size + 1)
        var position = 0
        
        System.arraycopy(IBEACON_PREFIX, 0, manufacturerData, position, IBEACON_PREFIX.size)
        position += IBEACON_PREFIX.size
        
        System.arraycopy(uuidBytes, 0, manufacturerData, position, uuidBytes.size)
        position += uuidBytes.size
        
        System.arraycopy(majorBytes, 0, manufacturerData, position, majorBytes.size)
        position += majorBytes.size
        
        System.arraycopy(minorBytes, 0, manufacturerData, position, minorBytes.size)
        position += minorBytes.size
        
        manufacturerData[position] = txPower.toByte()
        
        return manufacturerData
    }
    
    private fun getBytesFromUUID(uuid: UUID): ByteArray {
        val buffer = ByteBuffer.wrap(ByteArray(16))
        buffer.putLong(uuid.mostSignificantBits)
        buffer.putLong(uuid.leastSignificantBits)
        return buffer.array()
    }
    
    private fun shortToByteArray(value: Short): ByteArray {
        val bytes = ByteArray(2)
        bytes[0] = (value.toInt() shr 8).toByte()
        bytes[1] = value.toByte()
        return bytes
    }
} 