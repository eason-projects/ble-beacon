import CoreLocation
import SwiftUI

struct AdvancedContentView: View {
    // Get the scanner from the environment
    @EnvironmentObject private var scanner: AdvancedBeaconScanner

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Header with scan controls
                HStack {
                    Text("iBeacon Scanner")
                        .font(.headline)

                    Spacer()

                    // Scan button - only for iBeacons
                    Button(action: {
                        if scanner.isScanning {
                            scanner.stopScanning()
                        } else {
                            scanner.startScanning(forType: .iBeacon)
                        }
                    }) {
                        Text(scanner.isScanning ? "Stop Scan" : "Start Scan")
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(scanner.isScanning ? Color.red : Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .padding()

                // Error message if any
                if let errorMessage = scanner.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .padding()
                }

                // Scanning indicator
                if scanner.isScanning {
                    HStack {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle())
                        Text("Scanning for iBeacons...")
                            .padding(.leading, 8)
                    }
                    .padding()
                }

                // Information about iBeacon scanning
                if !scanner.isScanning {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("About iBeacon Scanning")
                            .font(.headline)
                            .padding(.bottom, 4)

                        Text(
                            "This app uses CoreLocation to scan for iBeacons, which provides more accurate and reliable detection than generic BLE scanning."
                        )
                        .font(.caption)
                        .foregroundColor(.secondary)

                        Text(
                            "Note: Only iBeacon scanning is supported with CoreLocation. For other beacon types, a different approach would be needed."
                        )
                        .font(.caption)
                        .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color(UIColor.secondarySystemBackground))
                    .cornerRadius(8)
                    .padding(.horizontal)
                }

                // List of beacons
                List {
                    ForEach(scanner.beacons) { beacon in
                        iBeaconRow(beacon: beacon)
                    }
                }
                .listStyle(PlainListStyle())

                // Empty state
                if scanner.beacons.isEmpty {
                    VStack {
                        Image(systemName: "antenna.radiowaves.left.and.right")
                            .font(.system(size: 50))
                            .foregroundColor(.gray)
                            .padding()

                        Text("No iBeacons Found")
                            .font(.headline)
                            .foregroundColor(.gray)

                        if !scanner.isScanning {
                            Text("Press Start Scan to find nearby iBeacons")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                                .padding()
                        } else {
                            Text("Scanning for iBeacons...")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                                .padding()
                        }
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color(UIColor.systemBackground))
                }

                // Status bar
                HStack {
                    Text("Found \(scanner.beacons.count) iBeacons")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Spacer()

                    if scanner.isScanning {
                        Text("Scanning for iBeacons...")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.horizontal)
                .padding(.vertical, 8)
                .background(Color(UIColor.secondarySystemBackground))
            }
            .navigationBarTitle("iBeacon Scanner", displayMode: .inline)
        }
    }
}

// Row view for an iBeacon
struct iBeaconRow: View {
    let beacon: GenericBeacon

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            // Header with UUID and proximity
            HStack {
                Text(beacon.uuid.uuidString.prefix(8) + "...")
                    .font(.headline)

                Spacer()

                // Proximity badge
                Text(proximityText(beacon.proximity))
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(proximityColor(beacon.proximity).opacity(0.2))
                    .foregroundColor(proximityColor(beacon.proximity))
                    .cornerRadius(8)

                // RSSI indicator
                HStack {
                    Image(systemName: rssiIcon(beacon.rssi))
                    Text("\(beacon.rssi) dBm")
                }
                .foregroundColor(rssiColor(beacon.rssi))
            }

            // Divider
            Divider()
                .padding(.vertical, 2)

            // Beacon details
            Text("UUID: \(beacon.uuid.uuidString)")
                .font(.caption)
                .foregroundColor(.secondary)

            Text("Major: \(beacon.major), Minor: \(beacon.minor)")
                .font(.caption)
                .foregroundColor(.secondary)

            Text("Distance: \(String(format: "%.2f", beacon.accuracy))m")
                .font(.caption)
                .foregroundColor(.secondary)

            // Timestamp
            Text("Last seen: \(formattedTimestamp(beacon.timestamp))")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .padding(.vertical, 4)
    }

    // Helper function to determine color based on RSSI
    private func rssiColor(_ rssi: Int) -> Color {
        if rssi > -50 {
            return .green
        } else if rssi > -70 {
            return .yellow
        } else {
            return .red
        }
    }

    // Helper function to determine icon based on RSSI
    private func rssiIcon(_ rssi: Int) -> String {
        if rssi > -50 {
            return "wifi"
        } else if rssi > -70 {
            return "wifi"
        } else {
            return "wifi.slash"
        }
    }

    // Helper function to get text for proximity
    private func proximityText(_ proximity: CLProximity) -> String {
        switch proximity {
        case .immediate:
            return "Immediate"
        case .near:
            return "Near"
        case .far:
            return "Far"
        case .unknown:
            return "Unknown"
        @unknown default:
            return "Unknown"
        }
    }

    // Helper function to get color for proximity
    private func proximityColor(_ proximity: CLProximity) -> Color {
        switch proximity {
        case .immediate:
            return .green
        case .near:
            return .blue
        case .far:
            return .orange
        case .unknown:
            return .gray
        @unknown default:
            return .gray
        }
    }

    // Helper function to format timestamp
    private func formattedTimestamp(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

#Preview {
    AdvancedContentView()
        .environmentObject(AdvancedBeaconScanner())
}
