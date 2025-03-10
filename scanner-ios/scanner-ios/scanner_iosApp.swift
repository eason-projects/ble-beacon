//
//  scanner_iosApp.swift
//  scanner-ios
//
//  Created by Eason Guo on 2025/3/10.
//

import CoreLocation
import SwiftUI

@main
struct scanner_iosApp: App {
    // Create the scanner as a StateObject at the app level
    @StateObject private var scanner = AdvancedBeaconScanner()

    var body: some Scene {
        WindowGroup {
            AdvancedContentView()
                .environmentObject(scanner)  // Pass the scanner to all views
                .onAppear {
                    // Request permissions when the app launches
                    let locationManager = CLLocationManager()
                    locationManager.requestAlwaysAuthorization()
                }
        }
    }
}
