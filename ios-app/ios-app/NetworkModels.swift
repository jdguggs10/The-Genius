//
//  NetworkModels.swift
//  ios-app
//
//  Created by AI Assistant on [Current Date].
//

import Foundation

// Re-using MessageRole from Message.swift, assuming it's accessible.
// If not, it should be defined here or imported appropriately.

/// Payload for a single message in the conversation history sent to the backend.
struct MessagePayload: Codable {
    let role: MessageRole // Assuming MessageRole is defined in Message.swift and accessible
    let content: String
}

/// The request structure for the /advice endpoint.
struct AdviceRequestPayload: Codable {
    let conversation: [MessagePayload]
    let model: String? // Optional: specify a model
    // Add other fields like 'players' or 'enable_web_search' if needed by the iOS app's logic
    // let players: [String]?
    // let enable_web_search: Bool?

    // Convenience initializer if you are creating this from existing Message structs
    init(conversation: [MessagePayload], model: String? = nil) {
        self.conversation = conversation
        self.model = model
    }
}

/// Represents an alternative piece of advice.
struct AdviceAlternativePayload: Codable {
    let player: String
    let reason: String?
}

/// The structure for the structured advice JSON response from the backend.
struct StructuredAdviceResponse: Codable, Identifiable {
    // Identifiable conformance if you plan to use it in SwiftUI lists directly with its own identity.
    // If the content itself provides identity (e.g. mainAdvice + timestamp implicitly), UUID might not be needed here.
    // For now, let's assume the whole response is one item. If it's part of a list of responses, add an id.
    var id = UUID() // Added for Identifiable, useful for UI lists

    let mainAdvice: String
    let reasoning: String?
    let confidenceScore: Double?
    let alternatives: [AdviceAlternativePayload]?
    let modelIdentifier: String?

    // CodingKeys can be used if your Swift property names differ from the JSON keys.
    // In this case, they match the Pydantic model if we use camelCase consistently in Swift for JSON keys like 'mainAdvice'.
    // If the backend sends snake_case (e.g., "main_advice"), then CodingKeys would be needed.
    // Based on Pydantic model definition, it will be snake_case by default unless aliased.
    // Let's assume backend will output camelCase for direct mapping or we adjust Pydantic.
    // For now, assuming direct mapping. If issues, add CodingKeys.
    enum CodingKeys: String, CodingKey {
        case mainAdvice = "main_advice"
        case reasoning
        case confidenceScore = "confidence_score"
        case alternatives
        case modelIdentifier = "model_identifier"
    }
}

// Example of an error structure if the backend sends a specific JSON error format
struct ErrorResponsePayload: Codable {
    let error: String
    let message: String
} 