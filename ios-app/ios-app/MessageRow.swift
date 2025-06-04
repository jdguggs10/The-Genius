//
//  MessageRow.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//

import SwiftUI

struct MessageRow: View {
    let message: Message
    
    var body: some View {
        if message.role == .user {
            UserBubble(message: message)
        } else {
            AssistantBubble(message: message)
        }
    }
}

#Preview {
    VStack {
        MessageRow(message: Message(
            id: UUID().uuidString,
            createdAt: Date(),
            role: .user,
            content: "This is a user message",
            attachments: []
        ))
        
        MessageRow(message: Message(
            id: UUID().uuidString,
            createdAt: Date(),
            role: .assistant,
            content: "This is an assistant response with some helpful advice.",
            attachments: []
        ))
    }
    .padding()
    .background(AppColors.backgroundColor)
} 