import SwiftUI

final class AppSettings: ObservableObject {
    @Published var apiKey: String = ""
    @Published var isLoggedIn: Bool = false
    @Published var defaultModelId: String = "gpt-3.5-turbo" // Default model ID
    let availableModels: [String] = ["gpt-3.5-turbo", "gpt-4"] // Example available models

    // Dark Mode preference
    enum DarkModeOption: String, CaseIterable, Identifiable {
        case on // Dark Mode On
        case off // Dark Mode Off (Light)
        case auto // Follow System

        var id: DarkModeOption { self }
        var displayName: String {
            switch self {
            case .on: return "On"
            case .off: return "Off"
            case .auto: return "Auto"
            }
        }
        var colorScheme: ColorScheme? {
            switch self {
            case .on: return .dark
            case .off: return .light
            case .auto: return nil
            }
        }
    }

    @Published var darkModeOption: DarkModeOption = .auto
} 