//
//  MessageRow.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//

import SwiftUI

struct MessageRow: View {
    let message: ChatMessage
    @EnvironmentObject private var viewModel: ChatViewModel
    
    var body: some View {
        if message.role == .user {
            UserBubble(message: message)
        } else {
            AssistantBubble(message: message)
                .environmentObject(viewModel)
        }
    }
}

#Preview {
    VStack {
        MessageRow(message: ChatMessage(
            id: UUID().uuidString,
            createdAt: Date(),
            role: .user,
            content: "This is a user message",
            attachments: []
        ))
        .environmentObject(ChatViewModel())

        MessageRow(message: ChatMessage(
            id: UUID().uuidString,
            createdAt: Date(),
            role: .assistant,
            content: "This is an assistant response with some helpful advice.",
            attachments: []
        ))
        .environmentObject(ChatViewModel())
    }
    .padding()
    .background(AppColors.backgroundColor)
}
