package com.example.blluetoothbeacon

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.blluetoothbeacon.ui.theme.BlluetoothBeaconTheme
import java.util.*

class MainActivity : ComponentActivity() {
    
    private lateinit var beaconService: BeaconService
    private lateinit var permissionHandler: PermissionHandler
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        beaconService = BeaconService(this)
        permissionHandler = PermissionHandler(this)
        
        // Set up listeners for advertising success and failure
        beaconService.setAdvertisingListeners(
            onSuccess = {
                runOnUiThread {
                    showToast("Beacon started successfully")
                }
            },
            onFailure = { errorCode, errorMessage ->
                runOnUiThread {
                    if (errorCode == BeaconService.ADVERTISE_FAILED_DATA_TOO_LARGE) {
                        showErrorDialog(
                            "Advertising Failed: Data Too Large",
                            "Your device has limitations on the size of advertising data. Would you like to try simplified mode?",
                            onConfirm = {
                                startSimplifiedBeacon()
                            }
                        )
                    } else {
                        showToast("Beacon failed to start: $errorMessage")
                    }
                }
            }
        )
        
        setContent {
            BlluetoothBeaconTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    BeaconScreen(
                        onStartBeacon = { uuid, major, minor, txPower, includeDeviceName, deviceName, serviceUuid, powerLevel, advertiseMode, useSimplifiedMode ->
                            if (useSimplifiedMode) {
                                startSimplifiedBeacon(uuid, major, minor, txPower, powerLevel, advertiseMode)
                            } else {
                                checkPermissionsAndStartBeacon(uuid, major, minor, txPower, includeDeviceName, deviceName, serviceUuid, powerLevel, advertiseMode)
                            }
                        },
                        onStopBeacon = {
                            beaconService.stopAdvertising()
                        },
                        beaconService = beaconService
                    )
                }
            }
        }
    }
    
    private fun startSimplifiedBeacon(
        uuid: UUID = UUID.fromString("E2C56DB5-DFFB-48D2-B060-D0F5A71096E0"),
        major: Int = 1,
        minor: Int = 100,
        txPower: Int = -59,
        powerLevel: Int = BeaconService.POWER_HIGH,
        advertiseMode: Int = BeaconService.MODE_LOW_LATENCY
    ) {
        permissionHandler.checkAndRequestPermissions(
            onGranted = {
                permissionHandler.checkAndRequestBluetoothEnable(
                    onEnabled = {
                        beaconService.startSimplifiedAdvertising(
                            uuid,
                            major,
                            minor,
                            txPower,
                            powerLevel,
                            advertiseMode
                        )
                    },
                    onDenied = {
                        showToast("Bluetooth must be enabled to use beacon")
                    }
                )
            },
            onDenied = {
                showToast("Required permissions must be granted to use beacon")
            }
        )
    }
    
    private fun checkPermissionsAndStartBeacon(
        uuid: UUID, 
        major: Int, 
        minor: Int, 
        txPower: Int,
        includeDeviceName: Boolean,
        deviceName: String?,
        serviceUuid: UUID?,
        powerLevel: Int,
        advertiseMode: Int
    ) {
        permissionHandler.checkAndRequestPermissions(
            onGranted = {
                permissionHandler.checkAndRequestBluetoothEnable(
                    onEnabled = {
                        beaconService.startAdvertisingWithOptions(
                            uuid, 
                            major, 
                            minor, 
                            txPower, 
                            includeDeviceName, 
                            deviceName, 
                            serviceUuid,
                            powerLevel,
                            advertiseMode
                        )
                    },
                    onDenied = {
                        showToast("Bluetooth must be enabled to use beacon")
                    }
                )
            },
            onDenied = {
                showToast("Required permissions must be granted to use beacon")
            }
        )
    }
    
    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
    
    private fun showErrorDialog(title: String, message: String, onConfirm: () -> Unit) {
        val builder = android.app.AlertDialog.Builder(this)
        builder.setTitle(title)
        builder.setMessage(message)
        builder.setPositiveButton("Yes") { _, _ ->
            onConfirm()
        }
        builder.setNegativeButton("No") { dialog, _ ->
            dialog.dismiss()
        }
        builder.show()
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BeaconScreen(
    onStartBeacon: (UUID, Int, Int, Int, Boolean, String?, UUID?, Int, Int, Boolean) -> Unit,
    onStopBeacon: () -> Unit,
    beaconService: BeaconService
) {
    var isBeaconActive by remember { mutableStateOf(false) }
    var uuidText by remember { mutableStateOf("E2C56DB5-DFFB-48D2-B060-D0F5A71096E0") }
    var majorText by remember { mutableStateOf("1") }
    var minorText by remember { mutableStateOf("100") }
    var txPowerText by remember { mutableStateOf("-59") }
    var includeDeviceName by remember { mutableStateOf(false) }
    var deviceNameText by remember { mutableStateOf("BLE-Beacon") }
    var includeServiceUuid by remember { mutableStateOf(false) }
    var serviceUuidText by remember { mutableStateOf("0000FFFF-0000-1000-8000-00805F9B34FB") }
    
    // Transmission power and advertising mode
    var selectedPowerLevel by remember { mutableStateOf(BeaconService.POWER_HIGH) }
    var selectedAdvertiseMode by remember { mutableStateOf(BeaconService.MODE_LOW_LATENCY) }
    
    // Simplified mode option
    var useSimplifiedMode by remember { mutableStateOf(false) }
    
    val scrollState = rememberScrollState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(scrollState),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "BLE Beacon Transmitter",
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 24.dp)
        )
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Beacon Configuration",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
                
                OutlinedTextField(
                    value = uuidText,
                    onValueChange = { uuidText = it },
                    label = { Text("UUID") },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp)
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedTextField(
                        value = majorText,
                        onValueChange = { majorText = it },
                        label = { Text("Major") },
                        modifier = Modifier
                            .weight(1f)
                            .padding(vertical = 4.dp)
                    )
                    
                    OutlinedTextField(
                        value = minorText,
                        onValueChange = { minorText = it },
                        label = { Text("Minor") },
                        modifier = Modifier
                            .weight(1f)
                            .padding(vertical = 4.dp)
                    )
                }
                
                OutlinedTextField(
                    value = txPowerText,
                    onValueChange = { txPowerText = it },
                    label = { Text("TX Power") },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp)
                )
            }
        }
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Identification Options",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                    
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Checkbox(
                            checked = useSimplifiedMode,
                            onCheckedChange = { 
                                useSimplifiedMode = it
                                if (useSimplifiedMode) {
                                    includeDeviceName = false
                                    includeServiceUuid = false
                                }
                            }
                        )
                        Text(
                            text = "Simplified Mode",
                            fontSize = 14.sp
                        )
                    }
                }
                
                if (useSimplifiedMode) {
                    Text(
                        text = "Simplified mode uses minimal advertising data for maximum compatibility. Device name and service UUID options are disabled.",
                        fontSize = 14.sp,
                        color = Color.Gray,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                } else {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Checkbox(
                            checked = includeDeviceName,
                            onCheckedChange = { includeDeviceName = it }
                        )
                        Text(
                            text = "Include Device Name",
                            modifier = Modifier.padding(start = 8.dp)
                        )
                    }
                    
                    AnimatedVisibility(visible = includeDeviceName) {
                        OutlinedTextField(
                            value = deviceNameText,
                            onValueChange = { deviceNameText = it },
                            label = { Text("Device Name") },
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp)
                        )
                    }
                    
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Checkbox(
                            checked = includeServiceUuid,
                            onCheckedChange = { includeServiceUuid = it }
                        )
                        Text(
                            text = "Custom Service UUID",
                            modifier = Modifier.padding(start = 8.dp)
                        )
                    }
                    
                    AnimatedVisibility(visible = includeServiceUuid) {
                        OutlinedTextField(
                            value = serviceUuidText,
                            onValueChange = { serviceUuidText = it },
                            label = { Text("Service UUID") },
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp)
                        )
                    }
                }
            }
        }
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Transmission Power",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
                
                Text(
                    text = "Select transmission power level:",
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
                
                // Power level radio buttons
                Column {
                    PowerLevelRadioButton(
                        label = beaconService.getPowerLevelDescription(BeaconService.POWER_ULTRA_LOW),
                        selected = selectedPowerLevel == BeaconService.POWER_ULTRA_LOW,
                        onClick = { selectedPowerLevel = BeaconService.POWER_ULTRA_LOW }
                    )
                    
                    PowerLevelRadioButton(
                        label = beaconService.getPowerLevelDescription(BeaconService.POWER_LOW),
                        selected = selectedPowerLevel == BeaconService.POWER_LOW,
                        onClick = { selectedPowerLevel = BeaconService.POWER_LOW }
                    )
                    
                    PowerLevelRadioButton(
                        label = beaconService.getPowerLevelDescription(BeaconService.POWER_MEDIUM),
                        selected = selectedPowerLevel == BeaconService.POWER_MEDIUM,
                        onClick = { selectedPowerLevel = BeaconService.POWER_MEDIUM }
                    )
                    
                    PowerLevelRadioButton(
                        label = beaconService.getPowerLevelDescription(BeaconService.POWER_HIGH),
                        selected = selectedPowerLevel == BeaconService.POWER_HIGH,
                        onClick = { selectedPowerLevel = BeaconService.POWER_HIGH }
                    )
                }
                
                Divider(modifier = Modifier.padding(vertical = 8.dp))
                
                Text(
                    text = "Advertising Mode:",
                    fontSize = 14.sp,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
                
                // Advertising mode radio buttons
                Column {
                    PowerLevelRadioButton(
                        label = beaconService.getAdvertiseModeDescription(BeaconService.MODE_LOW_POWER),
                        selected = selectedAdvertiseMode == BeaconService.MODE_LOW_POWER,
                        onClick = { selectedAdvertiseMode = BeaconService.MODE_LOW_POWER }
                    )
                    
                    PowerLevelRadioButton(
                        label = beaconService.getAdvertiseModeDescription(BeaconService.MODE_BALANCED),
                        selected = selectedAdvertiseMode == BeaconService.MODE_BALANCED,
                        onClick = { selectedAdvertiseMode = BeaconService.MODE_BALANCED }
                    )
                    
                    PowerLevelRadioButton(
                        label = beaconService.getAdvertiseModeDescription(BeaconService.MODE_LOW_LATENCY),
                        selected = selectedAdvertiseMode == BeaconService.MODE_LOW_LATENCY,
                        onClick = { selectedAdvertiseMode = BeaconService.MODE_LOW_LATENCY }
                    )
                }
                
                Text(
                    text = "Higher power increases range but uses more battery. Lower advertising interval (latency) increases detection speed but uses more battery.",
                    fontSize = 12.sp,
                    color = Color.Gray,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        StatusIndicator(isActive = isBeaconActive)
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = {
                if (isBeaconActive) {
                    onStopBeacon()
                    isBeaconActive = false
                } else {
                    try {
                        val uuid = UUID.fromString(uuidText)
                        val major = majorText.toIntOrNull() ?: 1
                        val minor = minorText.toIntOrNull() ?: 100
                        val txPower = txPowerText.toIntOrNull() ?: -59
                        
                        val deviceName = if (includeDeviceName && !useSimplifiedMode) deviceNameText else null
                        val serviceUuid = if (includeServiceUuid && !useSimplifiedMode) UUID.fromString(serviceUuidText) else null
                        
                        onStartBeacon(
                            uuid, 
                            major, 
                            minor, 
                            txPower, 
                            includeDeviceName && !useSimplifiedMode, 
                            deviceName, 
                            serviceUuid,
                            selectedPowerLevel,
                            selectedAdvertiseMode,
                            useSimplifiedMode
                        )
                        isBeaconActive = true
                    } catch (e: Exception) {
                        // Handle in the activity
                    }
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
        ) {
            Text(
                text = if (isBeaconActive) "Stop Beacon" else "Start Beacon",
                fontSize = 18.sp
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "This app broadcasts a BLE beacon signal that can be detected by other devices to estimate proximity using RSSI values.",
            fontSize = 14.sp,
            color = Color.Gray,
            modifier = Modifier.padding(bottom = 16.dp)
        )
    }
}

@Composable
fun PowerLevelRadioButton(label: String, selected: Boolean, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        RadioButton(
            selected = selected,
            onClick = onClick
        )
        Text(
            text = label,
            modifier = Modifier.padding(start = 8.dp)
        )
    }
}

@Composable
fun StatusIndicator(isActive: Boolean) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Center,
        modifier = Modifier.padding(8.dp)
    ) {
        Box(
            modifier = Modifier
                .size(16.dp)
                .padding(end = 8.dp)
                .background(
                    color = if (isActive) Color.Green else Color.Red,
                    shape = MaterialTheme.shapes.small
                )
        )
        
        Text(
            text = if (isActive) "Beacon Active" else "Beacon Inactive",
            fontSize = 16.sp,
            fontWeight = FontWeight.Medium
        )
    }
}