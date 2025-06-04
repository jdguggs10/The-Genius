//
//  Models.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//

import Foundation
import UIKit

// Message model representing a chat message
struct Message: Identifiable, Equatable {
    let id: String
    let createdAt: Date
    let role: MessageRole
    let content: String
    let attachments: [Attachment]
    var structuredAdvice: StructuredAdviceResponse?
    
    enum MessageRole: String, Codable {
        case user
        case assistant
    }
    
    struct Attachment: Equatable {
        let type: AttachmentType
        let data: Data?
        
        enum AttachmentType: String, Codable {
            case image
            case file
        }
    }
    
    static func == (lhs: Message, rhs: Message) -> Bool {
        return lhs.id == rhs.id
    }
}

// Structured advice format for AI responses
struct StructuredAdviceResponse: Codable {
    let mainAdvice: String
    let reasoning: String?
    let confidenceScore: Double?
    let alternatives: [Alternative]?
    let modelIdentifier: String?
    
    struct Alternative: Codable {
        let player: String
        let reason: String?
    }
    
    enum CodingKeys: String, CodingKey {
        case mainAdvice = "main_advice"
        case reasoning
        case confidenceScore = "confidence_score"
        case alternatives
        case modelIdentifier = "model_identifier"
    }
} 