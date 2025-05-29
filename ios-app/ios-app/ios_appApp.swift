//
//  ios_appApp.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI

@main
struct ios_appApp: App {
    var body: some Scene {
        WindowGroup {
            RootViewControllerWrapper()
                .ignoresSafeArea()
        }
    }
}

// A wrapper to host ContentView in a UIHostingController subclass with no input accessory view
struct RootViewControllerWrapper: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        class NoAccessoryHostingController: UIHostingController<ContentView> {
            override var inputAccessoryView: UIView? { UIView() }
            override var canBecomeFirstResponder: Bool { true }
        }
        return NoAccessoryHostingController(rootView: ContentView())
    }
    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
