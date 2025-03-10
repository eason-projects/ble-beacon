import SwiftUI
import Charts

// Data point for RSSI history
struct RSSIDataPoint: Identifiable {
    let id = UUID()
    let timestamp: Date
    let rssi: Int
}

// Chart container component
struct ChartContainer: View {
    let rssiHistory: [RSSIDataPoint]
    let chartLineColor: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Signal Strength History")
                .font(.headline)
                .padding(.horizontal)
            
            if rssiHistory.isEmpty {
                Text("No data available yet")
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding()
            } else {
                RSSIChartView(rssiHistory: rssiHistory, chartLineColor: chartLineColor)
                    .frame(height: 200)
                    .padding()
                    .background(Color(UIColor.secondarySystemBackground))
                    .cornerRadius(12)
                    .padding(.horizontal)
            }
            
            // Chart legend
            HStack(spacing: 16) {
                LegendItem(color: .green, label: "Strong (> -50 dBm)")
                LegendItem(color: .yellow, label: "Medium (> -70 dBm)")
                LegendItem(color: .red, label: "Weak (< -70 dBm)")
            }
            .padding(.horizontal)
        }
    }
}

// RSSI Chart View - Isolated to prevent unnecessary parent view updates
struct RSSIChartView: View {
    let rssiHistory: [RSSIDataPoint]
    let chartLineColor: Color
    
    var body: some View {
        Chart {
            ForEach(rssiHistory) { dataPoint in
                LineMark(
                    x: .value("Time", dataPoint.timestamp),
                    y: .value("RSSI", dataPoint.rssi)
                )
                .foregroundStyle(chartLineColor)
                .interpolationMethod(.catmullRom)
                
                AreaMark(
                    x: .value("Time", dataPoint.timestamp),
                    y: .value("RSSI", dataPoint.rssi)
                )
                .foregroundStyle(
                    .linearGradient(
                        colors: [chartLineColor.opacity(0.3), chartLineColor.opacity(0.0)],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .interpolationMethod(.catmullRom)
                
                // Add point markers for each signal received
                PointMark(
                    x: .value("Time", dataPoint.timestamp),
                    y: .value("RSSI", dataPoint.rssi)
                )
                .foregroundStyle(chartLineColor)
                .symbolSize(50)
            }
        }
        .chartYScale(domain: [-100, -20])
        .chartYAxis {
            AxisMarks(position: .leading)
        }
    }
}

// Legend item component
struct LegendItem: View {
    let color: Color
    let label: String
    
    var body: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(color)
                .frame(width: 8, height: 8)
            
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
} 