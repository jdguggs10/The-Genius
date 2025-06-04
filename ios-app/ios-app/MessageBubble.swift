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
    let message: Message
    
    var body: some View {
        MessageRow(message: message)
    }
}
