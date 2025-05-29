//
//  Message.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//
import Foundation
import SwiftUI

// Represents who sent the message
enum MessageRole: String, Codable {
    case user = "user"
    case assistant = "assistant"
    case system = "system" // System messages might be for instructions or errors not directly shown as bubbles
}

// Represents a single message in the chat
struct Message: Identifiable, Codable, Equatable {
    let id: UUID
    let role: MessageRole
    var content: String
    let timestamp: Date
    var attachments: [ChatAttachment]
    var structuredAdvice: StructuredAdviceResponse? // Added for assistant's structured response
    
    // Initializer for user and potentially simple system messages
    init(id: UUID = UUID(), role: MessageRole, content: String, attachments: [ChatAttachment] = [], structuredAdvice: StructuredAdviceResponse? = nil) {
        self.id = id
        self.role = role
        self.content = content
        self.timestamp = Date()
        self.attachments = attachments
        self.structuredAdvice = structuredAdvice // Initialize the new property
    }
    
    // Custom Equatable implementation - compare all relevant properties for SwiftUI reactivity
    static func == (lhs: Message, rhs: Message) -> Bool {
        return lhs.id == rhs.id && 
               lhs.content == rhs.content && 
               lhs.structuredAdvice == rhs.structuredAdvice &&
               lhs.attachments == rhs.attachments
    }
}

// Represents an attachment (like an image)
struct ChatAttachment: Identifiable, Codable, Equatable {
    let id: UUID
    let type: AttachmentType
    let data: Data?
    // Add other relevant attachment properties like filename, size if needed
    
    init(id: UUID = UUID(), type: AttachmentType, data: Data? = nil) {
        self.id = id
        self.type = type
        self.data = data
    }
    
    // Custom Equatable implementation
    static func == (lhs: ChatAttachment, rhs: ChatAttachment) -> Bool {
        return lhs.id == rhs.id
    }
}

enum AttachmentType: String, Codable {
    case image = "image"
    case file = "file"
    // Potentially add other types like pdf, audio, etc.
}
