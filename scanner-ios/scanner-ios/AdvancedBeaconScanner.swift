import Combine
import CoreLocation
import Foundation
import os.log

// Enum to represent different beacon types
enum BeaconType: String, CaseIterable {
    case iBeacon = "iBeacon"
    case eddystoneUID = "Eddystone-UID"
    case eddystoneURL = "Eddystone-URL"
    case altBeacon = "AltBeacon"
    case unknown = "Unknown"
}

// Generic beacon model to store information for all beacon types
struct GenericBeacon: Identifiable {
    let id = UUID()
    let type: BeaconType
    let uuid: UUID
    let major: CLBeaconMajorValue
    let minor: CLBeaconMinorValue
    let rssi: Int
    let accuracy: Double
    let proximity: CLProximity
    let timestamp: Date

    // Create from CLBeacon
    init(from beacon: CLBeacon) {
        self.type = .iBeacon
        self.uuid = beacon.uuid
        self.major = beacon.major.uint16Value
        self.minor = beacon.minor.uint16Value
        self.rssi = beacon.rssi
        self.accuracy = beacon.accuracy
        self.proximity = beacon.proximity
        self.timestamp = Date()
    }
}

// Advanced beacon scanner class that uses CoreLocation for iBeacon monitoring
class AdvancedBeaconScanner: NSObject, ObservableObject {
    // Published properties to update the UI
    @Published var beacons: [GenericBeacon] = []
    @Published var isScanning: Bool = false
    @Published var errorMessage: String?
    @Published var selectedBeaconType: BeaconType? = nil

    // CoreLocation manager
    private var locationManager: CLLocationManager!

    // Monitored beacon regions
    private var monitoredRegions: [CLBeaconRegion] = []

    // Common iBeacon UUIDs to monitor
    private let commonUUIDs = [
        UUID(uuidString: "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0")!,  // Apple AirLocate
        UUID(uuidString: "F7826DA6-4FA2-4E98-8024-BC5B71E0893E")!,  // Kontakt.io
        UUID(uuidString: "8EC76EA3-6668-48DA-9866-75BE8BC86F4D")!,  // Estimote
        UUID(uuidString: "B9407F30-F5F8-466E-AFF9-25556B57FE6D")!,  // Estimote
        UUID(uuidString: "D0D3FA86-CA76-45EC-9BD9-6AF4FB75CA44")!,  // Radius Networks
        UUID(uuidString: "A0B13730-3A9A-11E3-AA6E-0800200C9A66")!,  // Bluecats
        UUID(uuidString: "61687109-905F-4436-91F8-E602F514C96D")!,  // BlueSense
        UUID(uuidString: "E20A39F4-73F5-4BC4-A12F-17D1AD07A961")!,  // Radius Networks
        UUID(uuidString: "74278BDA-B644-4520-8F0C-720EAF059935")!,  // Gimbal
    ]

    // Debug logging
    private let logger = OSLog(
        subsystem: "com.yourapp.beaconscanner", category: "AdvancedBeaconScanner")

    // Initialize the scanner
    override init() {
        super.init()
        debugLog("AdvancedBeaconScanner initialized")

        // Initialize location manager
        locationManager = CLLocationManager()
        locationManager.delegate = self
        locationManager.requestAlwaysAuthorization()

        // Set up for best accuracy
        locationManager.desiredAccuracy = kCLLocationAccuracyBest

        debugLog("CLLocationManager created")
    }

    // Start scanning for beacons of a specific type
    func startScanning(forType beaconType: BeaconType? = nil) {
        guard beaconType == .iBeacon else {
            errorMessage = "Only iBeacon scanning is supported with CoreLocation"
            debugLog("Cannot start scanning: Only iBeacon scanning is supported with CoreLocation")
            return
        }

        selectedBeaconType = beaconType
        debugLog("Starting to scan for iBeacons")

        // Check authorization status
        let authStatus = CLLocationManager.authorizationStatus()
        guard authStatus == .authorizedAlways || authStatus == .authorizedWhenInUse else {
            errorMessage = "Location permission is required for beacon scanning"
            debugLog("Cannot start scanning: Location permission not granted")
            return
        }

        // Clear any previous error
        errorMessage = nil

        // Start monitoring and ranging for common beacon UUIDs
        startMonitoringBeacons()

        isScanning = true
        debugLog("Started scanning for iBeacons")
    }

    // Stop scanning for beacons
    func stopScanning() {
        // Stop monitoring all regions
        for region in monitoredRegions {
            locationManager.stopMonitoring(for: region)
            locationManager.stopRangingBeacons(in: region)
        }

        monitoredRegions.removeAll()
        isScanning = false
        debugLog("Stopped scanning for beacons")
    }

    // Start monitoring for common beacon UUIDs
    private func startMonitoringBeacons() {
        for uuid in commonUUIDs {
            let region = CLBeaconRegion(uuid: uuid, identifier: uuid.uuidString)
            region.notifyEntryStateOnDisplay = true
            region.notifyOnEntry = true
            region.notifyOnExit = true

            locationManager.startMonitoring(for: region)
            locationManager.startRangingBeacons(in: region)

            monitoredRegions.append(region)
            debugLog("Started monitoring region with UUID: \(uuid.uuidString)")
        }
    }

    // Debug logging helper
    private func debugLog(_ message: String) {
        // Format timestamp for console output
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "HH:mm:ss.SSS"
        let timestamp = dateFormatter.string(from: Date())

        // Print to Xcode console with clear formatting
        print("📡 BEACON [\(timestamp)] \(message)")
    }
}

// Extension to handle CLLocationManagerDelegate
extension AdvancedBeaconScanner: CLLocationManagerDelegate {
    // Handle authorization changes
    func locationManager(
        _ manager: CLLocationManager, didChangeAuthorization status: CLAuthorizationStatus
    ) {
        debugLog("Location authorization status changed to: \(status.rawValue)")

        switch status {
        case .authorizedAlways, .authorizedWhenInUse:
            debugLog("Location access authorized")
            if isScanning {
                startMonitoringBeacons()
            }
        case .denied, .restricted:
            errorMessage = "Location permission denied"
            isScanning = false
            debugLog("Location permission denied")
        case .notDetermined:
            debugLog("Location permission not determined yet")
        @unknown default:
            debugLog("Unknown authorization status: \(status.rawValue)")
        }
    }

    // Handle region monitoring events
    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        guard let beaconRegion = region as? CLBeaconRegion else { return }
        debugLog("Entered region: \(beaconRegion.identifier)")

        // Start ranging when in region
        locationManager.startRangingBeacons(in: beaconRegion)
    }

    func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        guard let beaconRegion = region as? CLBeaconRegion else { return }
        debugLog("Exited region: \(beaconRegion.identifier)")

        // Stop ranging when out of region
        locationManager.stopRangingBeacons(in: beaconRegion)
    }

    func locationManager(
        _ manager: CLLocationManager, didDetermineState state: CLRegionState, for region: CLRegion
    ) {
        guard let beaconRegion = region as? CLBeaconRegion else { return }

        switch state {
        case .inside:
            debugLog("Already inside region: \(beaconRegion.identifier)")
            locationManager.startRangingBeacons(in: beaconRegion)
        case .outside:
            debugLog("Already outside region: \(beaconRegion.identifier)")
        case .unknown:
            debugLog("Unknown state for region: \(beaconRegion.identifier)")
        @unknown default:
            debugLog("Unexpected state for region: \(beaconRegion.identifier)")
        }
    }

    // Handle beacon ranging
    func locationManager(
        _ manager: CLLocationManager, didRangeBeacons beacons: [CLBeacon], in region: CLBeaconRegion
    ) {
        if beacons.isEmpty {
            debugLog("No beacons found in region: \(region.identifier)")
            return
        }

        debugLog("Ranged \(beacons.count) beacons in region: \(region.identifier)")

        // Convert CLBeacons to our GenericBeacon model
        let genericBeacons = beacons.map { GenericBeacon(from: $0) }

        // Update our beacons list on the main thread
        DispatchQueue.main.async {
            // Replace beacons with the same UUID, major, and minor
            var updatedBeacons = self.beacons

            for newBeacon in genericBeacons {
                // Find if we already have this beacon
                if let index = updatedBeacons.firstIndex(where: {
                    $0.uuid == newBeacon.uuid && $0.major == newBeacon.major
                        && $0.minor == newBeacon.minor
                }) {
                    // Replace with updated beacon
                    updatedBeacons[index] = newBeacon
                } else {
                    // Add new beacon
                    updatedBeacons.append(newBeacon)
                }
            }

            // Sort by proximity/accuracy
            self.beacons = updatedBeacons.sorted {
                if $0.proximity != $1.proximity {
                    return $0.proximity.rawValue < $1.proximity.rawValue
                } else {
                    return $0.accuracy < $1.accuracy
                }
            }

            self.debugLog("Updated beacons list, count: \(self.beacons.count)")
        }
    }

    // Handle errors
    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        debugLog("Location manager failed with error: \(error.localizedDescription)")
        errorMessage = "Location error: \(error.localizedDescription)"
    }

    func locationManager(
        _ manager: CLLocationManager, monitoringDidFailFor region: CLRegion?, withError error: Error
    ) {
        let regionId = region?.identifier ?? "unknown"
        debugLog("Monitoring failed for region \(regionId): \(error.localizedDescription)")
    }

    func locationManager(
        _ manager: CLLocationManager, rangingBeaconsDidFailFor region: CLBeaconRegion,
        withError error: Error
    ) {
        debugLog(
            "Ranging beacons failed for region \(region.identifier): \(error.localizedDescription)")
    }
}
