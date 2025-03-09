package com.example.bluetoothbeacon;

import android.Manifest;
import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.AdvertiseCallback;
import android.bluetooth.le.AdvertiseData;
import android.bluetooth.le.AdvertiseSettings;
import android.bluetooth.le.BluetoothLeAdvertiser;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.ParcelUuid;
import android.os.Handler;
import android.os.Looper;
import android.text.InputType;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "BluetoothBeacon";
    private static final int REQUEST_ENABLE_BT = 1;
    private static final int REQUEST_PERMISSIONS = 2;
    private static final String PREFS_NAME = "BluetoothBeaconPrefs";
    private static final String PRESETS_KEY = "presets";

    private BluetoothAdapter bluetoothAdapter;
    private BluetoothLeAdvertiser advertiser;
    private AdvertiseCallback advertiseCallback;

    private Button startButton;
    private Button stopButton;
    private Button savePresetButton;
    private EditText uuidEditText;
    private TextView statusTextView;
    private RadioGroup powerRadioGroup;
    private RadioGroup modeRadioGroup;
    private Spinner presetSpinner;

    private boolean isAdvertising = false;
    private String defaultUuid = "11111111-2222-3333-4444-555555555555";
    private Handler handler = new Handler(Looper.getMainLooper());
    private List<String> presetNames = new ArrayList<>();
    private List<BeaconPreset> presets = new ArrayList<>();
    private ArrayAdapter<String> presetAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize UI components
        startButton = findViewById(R.id.start_button);
        stopButton = findViewById(R.id.stop_button);
        savePresetButton = findViewById(R.id.save_preset_button);
        uuidEditText = findViewById(R.id.uuid_edit_text);
        statusTextView = findViewById(R.id.status_text_view);
        powerRadioGroup = findViewById(R.id.power_radio_group);
        modeRadioGroup = findViewById(R.id.mode_radio_group);
        presetSpinner = findViewById(R.id.preset_spinner);

        // Set default UUID
        uuidEditText.setText(defaultUuid);

        // Initialize Bluetooth
        BluetoothManager bluetoothManager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
        if (bluetoothManager != null) {
            bluetoothAdapter = bluetoothManager.getAdapter();
        }

        // Check if Bluetooth is supported
        if (bluetoothAdapter == null) {
            statusTextView.setText("Bluetooth is not supported on this device");
            disableButtons();
            return;
        }

        // Check if BLE advertising is supported
        if (!checkBleAdvertisingSupport()) {
            statusTextView.setText("Bluetooth LE advertising is not supported on this device");
            disableButtons();
            return;
        }

        // Load presets
        loadPresets();

        // Setup preset spinner
        presetAdapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, presetNames);
        presetAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        presetSpinner.setAdapter(presetAdapter);
        
        // Add default preset if none exist
        if (presets.isEmpty()) {
            BeaconPreset defaultPreset = new BeaconPreset(
                    "Default",
                    defaultUuid,
                    AdvertiseSettings.ADVERTISE_TX_POWER_HIGH,
                    AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY
            );
            presets.add(defaultPreset);
            presetNames.add(defaultPreset.name);
            presetAdapter.notifyDataSetChanged();
            savePresets();
        }

        // Set up preset spinner listener
        presetSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                if (position >= 0 && position < presets.size()) {
                    loadPreset(presets.get(position));
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                // Do nothing
            }
        });

        // Set up button click listeners
        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startAdvertising();
            }
        });

        stopButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopAdvertising();
            }
        });
        
        savePresetButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showSavePresetDialog();
            }
        });

        // Initialize the advertise callback
        advertiseCallback = new AdvertiseCallback() {
            @Override
            public void onStartSuccess(AdvertiseSettings settingsInEffect) {
                super.onStartSuccess(settingsInEffect);
                isAdvertising = true;
                updateUI();
                Log.d(TAG, "Advertising started successfully");
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        String powerLevel = getSelectedPowerLevelName();
                        String mode = getSelectedModeName();
                        statusTextView.setText("Broadcasting: " + uuidEditText.getText().toString() + 
                                "\nPower: " + powerLevel + 
                                "\nMode: " + mode);
                        Toast.makeText(MainActivity.this, "Broadcasting started", Toast.LENGTH_SHORT).show();
                    }
                });
            }

            @Override
            public void onStartFailure(int errorCode) {
                super.onStartFailure(errorCode);
                isAdvertising = false;
                updateUI();
                String errorMessage = getAdvertisingErrorMessage(errorCode);
                Log.e(TAG, "Advertising failed to start: " + errorMessage);
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        statusTextView.setText("Failed to start broadcasting: " + errorMessage);
                        Toast.makeText(MainActivity.this, "Failed to start broadcasting", Toast.LENGTH_SHORT).show();
                    }
                });
            }
        };

        // Check and request permissions
        checkAndRequestPermissions();
    }

    @Override
    protected void onResume() {
        super.onResume();
        updateUI();
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (isAdvertising) {
            stopAdvertising();
        }
    }
    
    private void loadPreset(BeaconPreset preset) {
        if (isAdvertising) {
            return; // Don't change settings while broadcasting
        }
        
        uuidEditText.setText(preset.uuid);
        
        // Set power level
        switch (preset.powerLevel) {
            case AdvertiseSettings.ADVERTISE_TX_POWER_ULTRA_LOW:
                ((RadioButton) findViewById(R.id.power_ultra_low)).setChecked(true);
                break;
            case AdvertiseSettings.ADVERTISE_TX_POWER_LOW:
                ((RadioButton) findViewById(R.id.power_low)).setChecked(true);
                break;
            case AdvertiseSettings.ADVERTISE_TX_POWER_MEDIUM:
                ((RadioButton) findViewById(R.id.power_medium)).setChecked(true);
                break;
            case AdvertiseSettings.ADVERTISE_TX_POWER_HIGH:
                ((RadioButton) findViewById(R.id.power_high)).setChecked(true);
                break;
        }
        
        // Set mode
        switch (preset.advertiseMode) {
            case AdvertiseSettings.ADVERTISE_MODE_LOW_POWER:
                ((RadioButton) findViewById(R.id.mode_low_power)).setChecked(true);
                break;
            case AdvertiseSettings.ADVERTISE_MODE_BALANCED:
                ((RadioButton) findViewById(R.id.mode_balanced)).setChecked(true);
                break;
            case AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY:
                ((RadioButton) findViewById(R.id.mode_low_latency)).setChecked(true);
                break;
        }
    }
    
    private void showSavePresetDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Save Preset");
        
        // Set up the input
        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_TEXT);
        input.setHint("Enter preset name");
        builder.setView(input);
        
        // Set up the buttons
        builder.setPositiveButton("Save", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                String presetName = input.getText().toString().trim();
                if (presetName.isEmpty()) {
                    Toast.makeText(MainActivity.this, "Preset name cannot be empty", Toast.LENGTH_SHORT).show();
                    return;
                }
                
                // Create new preset
                BeaconPreset newPreset = new BeaconPreset(
                        presetName,
                        uuidEditText.getText().toString(),
                        getSelectedPowerLevel(),
                        getSelectedMode()
                );
                
                // Check if preset with this name already exists
                int existingIndex = -1;
                for (int i = 0; i < presets.size(); i++) {
                    if (presets.get(i).name.equals(presetName)) {
                        existingIndex = i;
                        break;
                    }
                }
                
                if (existingIndex >= 0) {
                    // Replace existing preset
                    presets.set(existingIndex, newPreset);
                } else {
                    // Add new preset
                    presets.add(newPreset);
                    presetNames.add(presetName);
                }
                
                // Save presets and update UI
                savePresets();
                presetAdapter.notifyDataSetChanged();
                presetSpinner.setSelection(presetNames.indexOf(presetName));
                
                Toast.makeText(MainActivity.this, "Preset saved", Toast.LENGTH_SHORT).show();
            }
        });
        
        builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                dialog.cancel();
            }
        });
        
        builder.show();
    }
    
    private void loadPresets() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String presetsJson = prefs.getString(PRESETS_KEY, "[]");
        
        try {
            JSONArray jsonArray = new JSONArray(presetsJson);
            presets.clear();
            presetNames.clear();
            
            for (int i = 0; i < jsonArray.length(); i++) {
                JSONObject jsonObject = jsonArray.getJSONObject(i);
                BeaconPreset preset = new BeaconPreset(
                        jsonObject.getString("name"),
                        jsonObject.getString("uuid"),
                        jsonObject.getInt("powerLevel"),
                        jsonObject.getInt("advertiseMode")
                );
                presets.add(preset);
                presetNames.add(preset.name);
            }
        } catch (JSONException e) {
            Log.e(TAG, "Error loading presets: " + e.getMessage());
        }
    }
    
    private void savePresets() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        SharedPreferences.Editor editor = prefs.edit();
        
        try {
            JSONArray jsonArray = new JSONArray();
            for (BeaconPreset preset : presets) {
                JSONObject jsonObject = new JSONObject();
                jsonObject.put("name", preset.name);
                jsonObject.put("uuid", preset.uuid);
                jsonObject.put("powerLevel", preset.powerLevel);
                jsonObject.put("advertiseMode", preset.advertiseMode);
                jsonArray.put(jsonObject);
            }
            
            editor.putString(PRESETS_KEY, jsonArray.toString());
            editor.apply();
        } catch (JSONException e) {
            Log.e(TAG, "Error saving presets: " + e.getMessage());
        }
    }

    private boolean checkBleAdvertisingSupport() {
        if (!getPackageManager().hasSystemFeature(PackageManager.FEATURE_BLUETOOTH_LE)) {
            return false;
        }
        
        if (bluetoothAdapter == null) {
            return false;
        }
        
        // Try to get the advertiser
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED) {
            return bluetoothAdapter.isMultipleAdvertisementSupported();
        }
        
        // If we can't check due to permissions, we'll assume it's supported and check again later
        return true;
    }
    
    private String getAdvertisingErrorMessage(int errorCode) {
        switch (errorCode) {
            case AdvertiseCallback.ADVERTISE_FAILED_ALREADY_STARTED:
                return "Advertising is already started";
            case AdvertiseCallback.ADVERTISE_FAILED_DATA_TOO_LARGE:
                return "Advertising data is too large";
            case AdvertiseCallback.ADVERTISE_FAILED_FEATURE_UNSUPPORTED:
                return "Advertising is not supported on this device";
            case AdvertiseCallback.ADVERTISE_FAILED_INTERNAL_ERROR:
                return "Internal error in the Bluetooth stack";
            case AdvertiseCallback.ADVERTISE_FAILED_TOO_MANY_ADVERTISERS:
                return "Too many advertisers already exist";
            default:
                return "Unknown error code: " + errorCode;
        }
    }

    private int getSelectedPowerLevel() {
        int selectedId = powerRadioGroup.getCheckedRadioButtonId();
        
        if (selectedId == R.id.power_ultra_low) {
            return AdvertiseSettings.ADVERTISE_TX_POWER_ULTRA_LOW;
        } else if (selectedId == R.id.power_low) {
            return AdvertiseSettings.ADVERTISE_TX_POWER_LOW;
        } else if (selectedId == R.id.power_medium) {
            return AdvertiseSettings.ADVERTISE_TX_POWER_MEDIUM;
        } else {
            return AdvertiseSettings.ADVERTISE_TX_POWER_HIGH;
        }
    }
    
    private String getSelectedPowerLevelName() {
        int selectedId = powerRadioGroup.getCheckedRadioButtonId();
        
        if (selectedId == R.id.power_ultra_low) {
            return "Ultra Low";
        } else if (selectedId == R.id.power_low) {
            return "Low";
        } else if (selectedId == R.id.power_medium) {
            return "Medium";
        } else {
            return "High";
        }
    }
    
    private int getSelectedMode() {
        int selectedId = modeRadioGroup.getCheckedRadioButtonId();
        
        if (selectedId == R.id.mode_low_power) {
            return AdvertiseSettings.ADVERTISE_MODE_LOW_POWER;
        } else if (selectedId == R.id.mode_balanced) {
            return AdvertiseSettings.ADVERTISE_MODE_BALANCED;
        } else {
            return AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY;
        }
    }
    
    private String getSelectedModeName() {
        int selectedId = modeRadioGroup.getCheckedRadioButtonId();
        
        if (selectedId == R.id.mode_low_power) {
            return "Low Power";
        } else if (selectedId == R.id.mode_balanced) {
            return "Balanced";
        } else {
            return "Low Latency";
        }
    }

    private void checkAndRequestPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            String[] permissions = {
                    Manifest.permission.BLUETOOTH_ADVERTISE,
                    Manifest.permission.BLUETOOTH_CONNECT,
                    Manifest.permission.ACCESS_FINE_LOCATION
            };
            
            boolean allPermissionsGranted = true;
            for (String permission : permissions) {
                if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                    allPermissionsGranted = false;
                    break;
                }
            }
            
            if (!allPermissionsGranted) {
                ActivityCompat.requestPermissions(this, permissions, REQUEST_PERMISSIONS);
                return;
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, REQUEST_PERMISSIONS);
                return;
            }
        }
        
        // Check if Bluetooth is enabled
        if (!bluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED) {
                startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_PERMISSIONS) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }
            
            if (allGranted) {
                // Check if Bluetooth is enabled
                if (!bluetoothAdapter.isEnabled()) {
                    Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                    if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED) {
                        startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
                    }
                }
            } else {
                statusTextView.setText("Required permissions not granted");
                disableButtons();
            }
        }
    }

    private void startAdvertising() {
        if (bluetoothAdapter == null || !bluetoothAdapter.isEnabled()) {
            Toast.makeText(this, "Bluetooth is not enabled", Toast.LENGTH_SHORT).show();
            return;
        }

        // Get the UUID from the EditText
        String uuidString = uuidEditText.getText().toString();
        if (uuidString.isEmpty()) {
            uuidString = defaultUuid;
            uuidEditText.setText(uuidString);
        }

        // Validate UUID format
        UUID uuid;
        try {
            uuid = UUID.fromString(uuidString);
        } catch (IllegalArgumentException e) {
            Toast.makeText(this, "Invalid UUID format", Toast.LENGTH_SHORT).show();
            return;
        }

        // Get the advertiser
        advertiser = bluetoothAdapter.getBluetoothLeAdvertiser();
        if (advertiser == null) {
            statusTextView.setText("Bluetooth LE advertising not supported on this device");
            return;
        }

        // Get selected power level and mode
        int powerLevel = getSelectedPowerLevel();
        int mode = getSelectedMode();

        // Create advertise settings
        AdvertiseSettings settings = new AdvertiseSettings.Builder()
                .setAdvertiseMode(mode)
                .setTxPowerLevel(powerLevel)
                .setConnectable(false)
                .setTimeout(0)
                .build();

        // Create advertise data
        AdvertiseData data = new AdvertiseData.Builder()
                .setIncludeDeviceName(false)
                .addServiceUuid(new ParcelUuid(uuid))
                .build();

        // Start advertising
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_ADVERTISE) == PackageManager.PERMISSION_GRANTED) {
            advertiser.startAdvertising(settings, data, advertiseCallback);
            statusTextView.setText("Starting broadcast...");
        } else {
            statusTextView.setText("Bluetooth advertise permission not granted");
        }
    }

    private void stopAdvertising() {
        if (advertiser != null && isAdvertising) {
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_ADVERTISE) == PackageManager.PERMISSION_GRANTED) {
                advertiser.stopAdvertising(advertiseCallback);
                isAdvertising = false;
                updateUI();
                statusTextView.setText("Broadcasting stopped");
                Toast.makeText(this, "Broadcasting stopped", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void updateUI() {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (isAdvertising) {
                    startButton.setEnabled(false);
                    stopButton.setEnabled(true);
                    uuidEditText.setEnabled(false);
                    powerRadioGroup.setEnabled(false);
                    for (int i = 0; i < powerRadioGroup.getChildCount(); i++) {
                        powerRadioGroup.getChildAt(i).setEnabled(false);
                    }
                    modeRadioGroup.setEnabled(false);
                    for (int i = 0; i < modeRadioGroup.getChildCount(); i++) {
                        modeRadioGroup.getChildAt(i).setEnabled(false);
                    }
                    presetSpinner.setEnabled(false);
                    savePresetButton.setEnabled(false);
                } else {
                    startButton.setEnabled(true);
                    stopButton.setEnabled(false);
                    uuidEditText.setEnabled(true);
                    powerRadioGroup.setEnabled(true);
                    for (int i = 0; i < powerRadioGroup.getChildCount(); i++) {
                        powerRadioGroup.getChildAt(i).setEnabled(true);
                    }
                    modeRadioGroup.setEnabled(true);
                    for (int i = 0; i < modeRadioGroup.getChildCount(); i++) {
                        modeRadioGroup.getChildAt(i).setEnabled(true);
                    }
                    presetSpinner.setEnabled(true);
                    savePresetButton.setEnabled(true);
                }
            }
        });
    }

    private void disableButtons() {
        startButton.setEnabled(false);
        stopButton.setEnabled(false);
        savePresetButton.setEnabled(false);
    }
    
    // Class to represent a beacon preset
    private static class BeaconPreset {
        String name;
        String uuid;
        int powerLevel;
        int advertiseMode;
        
        BeaconPreset(String name, String uuid, int powerLevel, int advertiseMode) {
            this.name = name;
            this.uuid = uuid;
            this.powerLevel = powerLevel;
            this.advertiseMode = advertiseMode;
        }
    }
} 