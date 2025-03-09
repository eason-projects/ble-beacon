package com.example.blluetoothbeacon

import android.Manifest
import android.app.Activity
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class PermissionHandler(private val activity: ComponentActivity) {
    
    companion object {
        private val REQUIRED_PERMISSIONS = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            arrayOf(
                Manifest.permission.BLUETOOTH_ADVERTISE,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.ACCESS_FINE_LOCATION
            )
        } else {
            arrayOf(
                Manifest.permission.BLUETOOTH,
                Manifest.permission.BLUETOOTH_ADMIN,
                Manifest.permission.ACCESS_FINE_LOCATION
            )
        }
    }
    
    private lateinit var permissionLauncher: ActivityResultLauncher<Array<String>>
    private lateinit var bluetoothEnableLauncher: ActivityResultLauncher<Intent>
    
    private var onPermissionsGranted: (() -> Unit)? = null
    private var onPermissionsDenied: (() -> Unit)? = null
    private var onBluetoothEnabled: (() -> Unit)? = null
    private var onBluetoothDenied: (() -> Unit)? = null
    
    init {
        permissionLauncher = activity.registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { permissions ->
            val allGranted = permissions.entries.all { it.value }
            if (allGranted) {
                onPermissionsGranted?.invoke()
            } else {
                onPermissionsDenied?.invoke()
            }
        }
        
        bluetoothEnableLauncher = activity.registerForActivityResult(
            ActivityResultContracts.StartActivityForResult()
        ) { result ->
            if (result.resultCode == Activity.RESULT_OK) {
                onBluetoothEnabled?.invoke()
            } else {
                onBluetoothDenied?.invoke()
            }
        }
    }
    
    fun checkAndRequestPermissions(
        onGranted: () -> Unit,
        onDenied: () -> Unit
    ) {
        this.onPermissionsGranted = onGranted
        this.onPermissionsDenied = onDenied
        
        if (hasRequiredPermissions()) {
            onGranted()
        } else {
            permissionLauncher.launch(REQUIRED_PERMISSIONS)
        }
    }
    
    fun checkAndRequestBluetoothEnable(
        onEnabled: () -> Unit,
        onDenied: () -> Unit
    ) {
        this.onBluetoothEnabled = onEnabled
        this.onBluetoothDenied = onDenied
        
        val bluetoothManager = activity.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager
        val bluetoothAdapter = bluetoothManager.adapter
        
        if (bluetoothAdapter == null) {
            onDenied()
            return
        }
        
        if (bluetoothAdapter.isEnabled) {
            onEnabled()
        } else {
            val enableBtIntent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
            bluetoothEnableLauncher.launch(enableBtIntent)
        }
    }
    
    private fun hasRequiredPermissions(): Boolean {
        return REQUIRED_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(activity, it) == PackageManager.PERMISSION_GRANTED
        }
    }
} 