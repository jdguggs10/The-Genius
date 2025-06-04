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
    
    @StateObject private var conversationManager = ConversationManager()
    @StateObject private var appSettings = AppSettings()
    
    init() {
        // App initialization - no keyboard prewarming needed
        setupAppLifecycleObservers()

        // Customize navigation bar title color to match appPrimaryFontColor
        let titleColor = UIColor(red: 61/255, green: 108/255, blue: 104/255, alpha: 1.0)
        let appearance = UINavigationBarAppearance()
        appearance.configureWithDefaultBackground()
        appearance.titleTextAttributes = [.foregroundColor: titleColor]
        appearance.largeTitleTextAttributes = [.foregroundColor: titleColor]
        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance
        UINavigationBar.appearance().compactAppearance = appearance
    }
    
    var body: some Scene {
        WindowGroup {
            RootViewControllerWrapper()
                .environmentObject(conversationManager)
                .environmentObject(appSettings)
                .ignoresSafeArea()
                .onAppear {
                    // Previous HangDetector related code was here
                }
                .onDisappear {
                    // Previous HangDetector related code was here
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
    @EnvironmentObject var conversationManager: ConversationManager
    @EnvironmentObject var appSettings: AppSettings
    
    // A hosting controller that disables the input accessory view
    class NoAccessoryHostingController: UIHostingController<AnyView> {
        override var inputAccessoryView: UIView? { UIView() }
        override var canBecomeFirstResponder: Bool { true }
    }
    
    func makeUIViewController(context: Context) -> UIViewController {
        let contentView = ContentView()
            .environmentObject(conversationManager)
            .environmentObject(appSettings)
            .preferredColorScheme(appSettings.darkModeOption.colorScheme)
        
        return NoAccessoryHostingController(rootView: AnyView(contentView))
    }
    
    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {
        // Update the rootView to reflect changes in dark mode preference
        if let hostingController = uiViewController as? NoAccessoryHostingController {
            hostingController.rootView = AnyView(
                ContentView()
                    .environmentObject(conversationManager)
                    .environmentObject(appSettings)
                    .preferredColorScheme(appSettings.darkModeOption.colorScheme)
            )
        }
    }
}
