import SwiftUI
import Charts
import CoreLocation

// Detail view for a selected beacon
struct BeaconDetailView: View, Equatable {
    let beacon: GenericBeacon
    @EnvironmentObject private var scanner: AdvancedBeaconScanner
    @State private var rssiHistory: [RSSIDataPoint] = []
    @State private var timer: Timer? = nil
    
    // Implement Equatable to prevent unnecessary view updates
    static func == (lhs: BeaconDetailView, rhs: BeaconDetailView) -> Bool {
        return lhs.beacon.id == rhs.beacon.id
    }
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                // Beacon info card
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text("iBeacon \(beacon.major)/\(beacon.minor)")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        Spacer()
                        
                        // Proximity indicator
                        Text(proximityText(beacon.proximity))
                            .font(.caption)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(proximityColor(beacon.proximity).opacity(0.2))
                            .foregroundColor(proximityColor(beacon.proximity))
                            .cornerRadius(8)
                    }
                    
                    Divider()
                    
                    // Beacon details
                    Group {
                        DetailRow(label: "UUID", value: beacon.uuid.uuidString)
                        DetailRow(label: "Major", value: "\(beacon.major)")
                        DetailRow(label: "Minor", value: "\(beacon.minor)")
                        DetailRow(label: "RSSI", value: "\(getCurrentRSSI()) dBm")
                        DetailRow(label: "Distance", value: String(format: "%.2f meters", getCurrentAccuracy()))
                        DetailRow(label: "Last seen", value: formattedTimestamp(getCurrentTimestamp()))
                    }
                }
                .padding()
                .background(Color(UIColor.secondarySystemBackground))
                .cornerRadius(12)
                .padding(.horizontal)
                
                // Signal strength chart
                ChartContainer(rssiHistory: rssiHistory, chartLineColor: chartLineColor())
            }
            .padding(.vertical)
        }
        .navigationTitle("Beacon Details")
        .onAppear {
            // Start collecting data
            startMonitoring()
        }
        .onDisappear {
            // Stop the timer when view disappears
            stopMonitoring()
        }
    }
    
    // Start collecting RSSI data
    private func startMonitoring() {
        // Add initial data point
        rssiHistory.append(RSSIDataPoint(timestamp: Date(), rssi: getCurrentRSSI()))
        
        // Set up timer to collect data every second
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { _ in
            // Only add new data if we're scanning
            if self.scanner.isScanning {
                // Use DispatchQueue.main.async to batch UI updates
                DispatchQueue.main.async {
                    self.rssiHistory.append(RSSIDataPoint(timestamp: Date(), rssi: self.getCurrentRSSI()))
                    
                    // Limit history to last 60 seconds
                    if self.rssiHistory.count > 60 {
                        self.rssiHistory.removeFirst(self.rssiHistory.count - 60)
                    }
                }
            }
        }
    }
    
    // Stop collecting RSSI data
    private func stopMonitoring() {
        timer?.invalidate()
        timer = nil
    }
    
    // Get current RSSI from the scanner
    private func getCurrentRSSI() -> Int {
        if let updatedBeacon = scanner.beacons.first(where: { 
            $0.uuid == beacon.uuid && $0.major == beacon.major && $0.minor == beacon.minor 
        }) {
            return updatedBeacon.rssi
        }
        return beacon.rssi
    }
    
    // Get current accuracy from the scanner
    private func getCurrentAccuracy() -> Double {
        if let updatedBeacon = scanner.beacons.first(where: { 
            $0.uuid == beacon.uuid && $0.major == beacon.major && $0.minor == beacon.minor 
        }) {
            return updatedBeacon.accuracy
        }
        return beacon.accuracy
    }
    
    // Get current timestamp from the scanner
    private func getCurrentTimestamp() -> Date {
        if let updatedBeacon = scanner.beacons.first(where: { 
            $0.uuid == beacon.uuid && $0.major == beacon.major && $0.minor == beacon.minor 
        }) {
            return updatedBeacon.timestamp
        }
        return beacon.timestamp
    }
    
    // Helper function to get color for chart line
    private func chartLineColor() -> Color {
        let rssi = getCurrentRSSI()
        if rssi > -50 {
            return .green
        } else if rssi > -70 {
            return .yellow
        } else {
            return .red
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

// Detail row component
struct DetailRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack(alignment: .top) {
            Text(label)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .frame(width: 80, alignment: .leading)
            
            Text(value)
                .font(.subheadline)
                .multilineTextAlignment(.leading)
            
            Spacer()
        }
        .padding(.vertical, 2)
    }
}

#Preview {
    // For preview only, we'll use a placeholder
    struct PreviewPlaceholder: View {
        var body: some View {
            VStack {
                Text("Beacon Detail View")
                    .font(.title)
                Text("This is a preview of how the beacon detail view will look")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .padding()
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("Signal Strength History")
                        .font(.headline)
                        .padding(.bottom)
                    
                    // Mock chart
                    ZStack {
                        // Background grid
                        VStack(spacing: 0) {
                            ForEach(0..<5) { _ in
                                Divider()
                                Spacer()
                            }
                        }
                        
                        // Mock line
                        Path { path in
                            path.move(to: CGPoint(x: 0, y: 100))
                            path.addCurve(
                                to: CGPoint(x: 300, y: 80),
                                control1: CGPoint(x: 100, y: 50),
                                control2: CGPoint(x: 200, y: 120)
                            )
                        }
                        .stroke(Color.green, lineWidth: 2)
                        
                        // Mock data points
                        Circle()
                            .fill(Color.green)
                            .frame(width: 8, height: 8)
                            .position(x: 0, y: 100)
                        
                        Circle()
                            .fill(Color.green)
                            .frame(width: 8, height: 8)
                            .position(x: 75, y: 60)
                            
                        Circle()
                            .fill(Color.green)
                            .frame(width: 8, height: 8)
                            .position(x: 150, y: 90)
                            
                        Circle()
                            .fill(Color.green)
                            .frame(width: 8, height: 8)
                            .position(x: 225, y: 70)
                            
                        Circle()
                            .fill(Color.green)
                            .frame(width: 8, height: 8)
                            .position(x: 300, y: 80)
                    }
                    .frame(height: 150)
                    .padding()
                    .background(Color(UIColor.secondarySystemBackground))
                    .cornerRadius(12)
                }
                .padding()
            }
            .padding()
        }
    }
    
    return NavigationView {
        PreviewPlaceholder()
    }
}
