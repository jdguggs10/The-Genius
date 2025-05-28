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
    case system = "system"
}

// Represents a single message in the chat
struct Message: Identifiable, Codable {
    let id: UUID
    let role: MessageRole
    var content: String
    let timestamp: Date
    var attachments: [ChatAttachment]
    
    init(id: UUID = UUID(), role: MessageRole, content: String, attachments: [ChatAttachment] = []) {
        self.id = id
        self.role = role
        self.content = content
        self.timestamp = Date()
        self.attachments = attachments
    }
}

// Represents an attachment (like an image)
struct ChatAttachment: Identifiable, Codable {
    let id: UUID
    let type: AttachmentType
    let data: Data?
    
    init(id: UUID = UUID(), type: AttachmentType, data: Data? = nil) {
        self.id = id
        self.type = type
        self.data = data
    }
}

enum AttachmentType: String, Codable {
    case image = "image"
    case file = "file"
}
