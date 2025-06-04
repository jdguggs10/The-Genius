//
//  MessageBubble.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//
import SwiftUI

// This file is now a simple wrapper for backward compatibility
// New code should use MessageRow directly
struct MessageBubble: View {
    let message: ChatMessage
    @EnvironmentObject private var viewModel: ChatViewModel

    var body: some View {
        MessageRow(message: message)
            .environmentObject(viewModel)
    }
}
