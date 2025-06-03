//
//  HangDetector.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import Foundation
import SwiftUI
import os.log

/// Proactive hang detection and prevention utility
/// Implements patterns from the iOS Hang Debugging Guide
@MainActor
class HangDetector: ObservableObject {
    static let shared = HangDetector()
    
    // MARK: - Configuration
    private let hangThreshold: TimeInterval = 0.1 // 100ms as per Apple guidelines
    private let memoryPressureThreshold: UInt64 = 100_000_000 // 100MB
    private let monitoringQueue = DispatchQueue(label: "hang.detector", qos: .utility)
    
    // MARK: - State
    @Published var isMonitoring = false
    @Published var hangCount = 0
    @Published var memoryPressureWarnings = 0
    
    private var monitoringTimer: Timer?
    private var memoryPressureSource: DispatchSourceMemoryPressure?
    
    // MARK: - Logger
    private let logger = Logger(subsystem: "com.yourapp.hangdetection", category: "performance")
    
    // MARK: - Hang Detection
    func startMonitoring() {
        guard !isMonitoring else { return }
        isMonitoring = true
        
        startHangDetection()
        startMemoryPressureMonitoring()
        
        logger.info("Hang detection monitoring started")
    }
    
    func stopMonitoring() {
        guard isMonitoring else { return }
        isMonitoring = false
        
        monitoringTimer?.invalidate()
        monitoringTimer = nil
        
        memoryPressureSource?.cancel()
        memoryPressureSource = nil
        
        logger.info("Hang detection monitoring stopped")
    }
    
    private func startHangDetection() {
        monitoringQueue.async { [weak self] in
            guard let self = self else { return }
            
            // Define a timeout slightly longer than the hangThreshold for the semaphore
            let semaphoreTimeoutMilliseconds = Int((self.hangThreshold * 2.5) * 1000)
            
            while true {
                // Check monitoring state synchronously using a semaphore
                let stateSemaphore = DispatchSemaphore(value: 0)
                var shouldContinue = false
                
                DispatchQueue.main.async {
                    shouldContinue = self.isMonitoring
                    stateSemaphore.signal()
                }
                
                stateSemaphore.wait()
                
                guard shouldContinue else { break }
                
                let semaphore = DispatchSemaphore(value: 0)
                let startTime = CFAbsoluteTimeGetCurrent()
                
                DispatchQueue.main.async {
                    semaphore.signal()
                }
                
                // Wait for the semaphore with a timeout
                let waitResult = semaphore.wait(timeout: .now() + .milliseconds(semaphoreTimeoutMilliseconds))
                let duration = CFAbsoluteTimeGetCurrent() - startTime
                
                if waitResult == .timedOut {
                    // Main thread did not respond within the timeout, indicating a severe hang or deadlock
                    Task { @MainActor in
                        self.handleSevereHangDetected(duration: duration)
                    }
                } else if duration > self.hangThreshold {
                    // Main thread responded, but was slower than the threshold
                    Task { @MainActor in
                        self.handleHangDetected(duration: duration)
                    }
                }
                
                // Adjust sleep to account for the time spent waiting, aiming for roughly 50ms cycle
                let remainingSleepTime = max(0, 0.05 - duration)
                Thread.sleep(forTimeInterval: remainingSleepTime)
            }
        }
    }
    
    private func startMemoryPressureMonitoring() {
        let source = DispatchSource.makeMemoryPressureSource(
            eventMask: [.warning, .critical],
            queue: .main
        )
        
        source.setEventHandler { [weak self] in
            guard let self = self else { return }
            let event = source.mask
            
            Task { @MainActor in
                self.memoryPressureWarnings += 1
                
                if event.contains(.critical) {
                    self.logger.error("Critical memory pressure detected - hang risk high")
                    self.handleCriticalMemoryPressure()
                } else if event.contains(.warning) {
                    self.logger.warning("Memory pressure warning")
                    self.handleMemoryPressureWarning()
                }
            }
        }
        
        source.resume()
        self.memoryPressureSource = source
    }
    
    // MARK: - Event Handlers
    private func handleHangDetected(duration: TimeInterval) {
        hangCount += 1
        logger.error("Main thread hang detected: \(String(format: "%.3f", duration))s")
        
        // Add to crash reporting if available (Sentry, Firebase, etc.)
        // logHangToAnalytics(duration: duration)
        
        #if DEBUG
        print("🚨 HANG DETECTED: \(String(format: "%.3f", duration))s")
        #endif
    }
    
    // New handler for severe hangs (when semaphore times out)
    private func handleSevereHangDetected(duration: TimeInterval) {
        hangCount += 1 // Increment hang count for severe hangs as well
        logger.critical("CRITICAL: Main thread UNRESPONSIVE (timeout after \(String(format: "%.3f", duration))s). Potential deadlock.")
        
        // Add to crash reporting with higher severity
        // logSevereHangToAnalytics(duration: duration)

        #if DEBUG
        print("🚨🚨 SEVERE HANG DETECTED (TIMEOUT): Main thread unresponsive for at least \(String(format: "%.3f", duration))s. Potential deadlock. 🚨🚨")
        #endif
        // For a very severe hang, a watchdog might typically terminate the app
        // or attempt more drastic recovery/logging if possible from a background thread.
        // However, from this isolated detector, logging is the primary action.
    }
    
    private func handleMemoryPressureWarning() {
        // Force garbage collection
        autoreleasepool {
            // Clear caches if available
            URLCache.shared.removeAllCachedResponses()
        }
        
        logger.warning("Memory pressure warning handled")
    }
    
    private func handleCriticalMemoryPressure() {
        // Emergency memory cleanup
        autoreleasepool {
            URLCache.shared.removeAllCachedResponses()
            // Clear image caches, temporary data, etc.
        }
        
        logger.error("Critical memory pressure handled")
    }
    
    // MARK: - Performance Measurement
    func measureAsyncOperation<T>(
        operation: () async throws -> T,
        description: String = "Operation"
    ) async rethrows -> T {
        let startTime = CFAbsoluteTimeGetCurrent()
        let result = try await operation()
        let duration = CFAbsoluteTimeGetCurrent() - startTime
        
        if duration > hangThreshold {
            logger.warning("\(description) took \(String(format: "%.3f", duration))s - exceeds threshold")
        }
        
        return result
    }
    
    func measureMainThreadOperation<T>(
        operation: () throws -> T,
        description: String = "Operation"
    ) rethrows -> T {
        let startTime = CFAbsoluteTimeGetCurrent()
        let result = try operation()
        let duration = CFAbsoluteTimeGetCurrent() - startTime
        
        if duration > hangThreshold {
            logger.warning("\(description) took \(String(format: "%.3f", duration))s on main thread")
        }
        
        return result
    }
}

// MARK: - SwiftUI Integration
extension HangDetector {
    var statusText: String {
        guard isMonitoring else { return "Monitoring disabled" }
        return "Hangs: \(hangCount) | Memory warnings: \(memoryPressureWarnings)"
    }
}

// MARK: - Debug View
#if DEBUG
struct HangDetectorDebugView: View {
    @StateObject private var hangDetector = HangDetector.shared
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Hang Detection Debug")
                .font(.headline)
            
            Text(hangDetector.statusText)
                .font(.caption)
                .foregroundColor(.secondary)
            
            HStack {
                Button(hangDetector.isMonitoring ? "Stop" : "Start") {
                    if hangDetector.isMonitoring {
                        hangDetector.stopMonitoring()
                    } else {
                        hangDetector.startMonitoring()
                    }
                }
                .buttonStyle(.bordered)
                
                Button("Test Hang") {
                    // Simulate a hang for testing
                    Thread.sleep(forTimeInterval: 0.15)
                }
                .buttonStyle(.bordered)
                .foregroundColor(.red)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
}
#endif 