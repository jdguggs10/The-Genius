//
//  ios_appApp.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI
import UIKit

@main
struct ios_appApp: App {
    
    init() {
        // App initialization - no keyboard prewarming needed
        setupAppLifecycleObservers()
    }
    
    var body: some Scene {
        WindowGroup {
            RootViewControllerWrapper()
                .ignoresSafeArea()
                .onAppear {
                    // Start hang detection monitoring
                    Task { @MainActor in
                        HangDetector.shared.startMonitoring()
                    }
                }
                .onDisappear {
                    // Stop monitoring when app goes to background
                    Task { @MainActor in
                        HangDetector.shared.stopMonitoring()
                    }
                }
        }
    }
    
    // MARK: - App Lifecycle Management
    private func setupAppLifecycleObservers() {
        // Basic app lifecycle observation without keyboard prewarming
        NotificationCenter.default.addObserver(
            forName: UIApplication.didBecomeActiveNotification,
            object: nil,
            queue: .main
        ) { _ in
            // App became active - can add any needed setup here
        }
        
        NotificationCenter.default.addObserver(
            forName: UIApplication.willEnterForegroundNotification,
            object: nil,
            queue: .main
        ) { _ in
            // App will enter foreground - can add any needed setup here
        }
        
        NotificationCenter.default.addObserver(
            forName: UIApplication.didFinishLaunchingNotification,
            object: nil,
            queue: .main
        ) { _ in
            // App finished launching - can add any needed setup here
        }
    }
}

// A wrapper to host ContentView in a UIHostingController subclass with no input accessory view
struct RootViewControllerWrapper: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        let conversationManager = ConversationManager()
        let contentView = ContentView()
            .environmentObject(conversationManager)
        
        class NoAccessoryHostingController<Content: View>: UIHostingController<Content> {
            override var inputAccessoryView: UIView? { UIView() }
            override var canBecomeFirstResponder: Bool { true }
        }
        
        return NoAccessoryHostingController(rootView: contentView)
    }
    
    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
