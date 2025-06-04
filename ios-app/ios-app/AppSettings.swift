import SwiftUI

final class AppSettings: ObservableObject {
    @Published var apiKey: String = ""
    @Published var isLoggedIn: Bool = false
    @Published var defaultModelId: String = "gpt-3.5-turbo" // Default model ID
    let availableModels: [String] = ["gpt-3.5-turbo", "gpt-4"] // Example available models
} 