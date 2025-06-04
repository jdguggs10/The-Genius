//
//  Models.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//

import Foundation
import UIKit

// Chat message model representing a chat message
struct ChatMessage: Identifiable, Equatable, Codable {
    let id: String
    let createdAt: Date
    let role: MessageRole
    var content: String
    let attachments: [Attachment]
    var structuredAdvice: StructuredAdviceResponse?
    
    enum MessageRole: String, Codable {
        case user
        case assistant
    }
    
    struct Attachment: Equatable, Codable {
        let type: AttachmentType
        let data: Data?
        
        enum AttachmentType: String, Codable {
            case image
            case file
        }
    }
    
    static func == (lhs: ChatMessage, rhs: ChatMessage) -> Bool {
        return lhs.id == rhs.id
    }
}

// Removed duplicate StructuredAdviceResponse struct - using the one from NetworkModels.swift 