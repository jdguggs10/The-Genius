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
    var body: some Scene {
        WindowGroup {
            RootViewControllerWrapper()
                .ignoresSafeArea()
                .onAppear {
                    // Start hang detection monitoring
                    Task { @MainActor in
                        HangDetector.shared.startMonitoring()
                    }
                    
                    // Pre-warm keyboard at app launch for instant response
                    Task { @MainActor in
                        try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 second delay to let app settle
                        KeyboardPrewarmer.shared.prewarmKeyboard()
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
            
            override func viewDidLoad() {
                super.viewDidLoad()
                
                // Additional keyboard pre-warming at the root level
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                    KeyboardPrewarmer.shared.prewarmKeyboard()
                }
            }
            
            override func viewWillAppear(_ animated: Bool) {
                super.viewWillAppear(animated)
                
                // Pre-warm keyboard when root view appears for instant text input
                DispatchQueue.main.async {
                    KeyboardPrewarmer.shared.prewarmKeyboard()
                }
            }
        }
        
        return NoAccessoryHostingController(rootView: contentView)
    }
    
    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
