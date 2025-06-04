//
//  NetworkModels.swift
//  ios-app
//
//  Created by AI Assistant on [Current Date].
//

import Foundation

// Re-using MessageRole from ChatMessage in Models.swift
// If not, it should be defined here or imported appropriately.

/// Payload for a single message in the conversation history sent to the backend.
struct MessagePayload: Codable {
    let role: ChatMessage.MessageRole
    let content: String
}

/// The request structure for the /advice endpoint.
struct AdviceRequestPayload: Codable {
    let conversation: [MessagePayload]?
    let model: String? // Optional: specify a model
    let previousResponseId: String? // Add support for previous_response_id
    let enableWebSearch: Bool? // Optional: enable web search
    
    // Convenience initializer for new conversations (without previous_response_id)
    init(conversation: [MessagePayload], model: String? = nil, enableWebSearch: Bool? = nil) {
        self.conversation = conversation
        self.model = model
        self.previousResponseId = nil
        self.enableWebSearch = enableWebSearch
    }
    
    // Convenience initializer for continuing conversations (with previous_response_id)
    init(userMessage: String, previousResponseId: String, model: String? = nil, enableWebSearch: Bool? = nil) {
        // When using previous_response_id, we only need to send the new user message
        self.conversation = [MessagePayload(role: .user, content: userMessage)]
        self.model = model
        self.previousResponseId = previousResponseId
        self.enableWebSearch = enableWebSearch
    }

    enum CodingKeys: String, CodingKey {
        case conversation
        case model
        case previousResponseId = "previous_response_id"
        case enableWebSearch = "enable_web_search"
    }
}

/// Represents an alternative piece of advice.
struct Alternative: Codable, Equatable {
    let player: String
    let reason: String?
}

/// The structure for the structured advice JSON response from the backend.
struct StructuredAdviceResponse: Codable, Identifiable, Equatable {
    // Identifiable conformance if you plan to use it in SwiftUI lists directly with its own identity.
    // If the content itself provides identity (e.g. mainAdvice + timestamp implicitly), UUID might not be needed here.
    // For now, let's assume the whole response is one item. If it's part of a list of responses, add an id.
    var id = UUID() // Added for Identifiable, useful for UI lists

    let mainAdvice: String
    let reasoning: String?
    let confidenceScore: Double?
    let alternatives: [Alternative]?
    let modelIdentifier: String?
    let responseId: String? // Add response ID for future reference

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
        case responseId = "response_id"
    }
    
    // Custom Equatable implementation - compare content for SwiftUI reactivity
    static func == (lhs: StructuredAdviceResponse, rhs: StructuredAdviceResponse) -> Bool {
        return lhs.mainAdvice == rhs.mainAdvice &&
               lhs.reasoning == rhs.reasoning &&
               lhs.confidenceScore == rhs.confidenceScore &&
               lhs.alternatives == rhs.alternatives &&
               lhs.modelIdentifier == rhs.modelIdentifier &&
               lhs.responseId == rhs.responseId
    }
}

/// Error response structure from the backend.
struct ErrorResponsePayload: Codable {
    let error: String
    let message: String
} 