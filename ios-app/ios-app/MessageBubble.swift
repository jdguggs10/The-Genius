//
//  MessageBubble.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//
import SwiftUI

struct MessageBubble: View {
    let message: Message
    
    var body: some View {
        HStack {
            if message.role == .user {
                Spacer()
            }
            
            VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 4) {
                // Message content
                Text(message.content)
                    .padding(12)
                    .background(bubbleColor)
                    .foregroundColor(textColor)
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                
                // Timestamp
                Text(timeString)
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            if message.role == .assistant {
                Spacer()
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 4)
    }
    
    private var bubbleColor: Color {
        switch message.role {
        case .user:
            return Color.blue
        case .assistant:
            return Color.gray.opacity(0.2)  // This works on all iOS versions
        case .system:
            return Color.gray.opacity(0.1)  // This works on all iOS versions
        }
    }
    
    private var textColor: Color {
        message.role == .user ? .white : .primary
    }
    
    private var timeString: String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: message.timestamp)
    }
}
