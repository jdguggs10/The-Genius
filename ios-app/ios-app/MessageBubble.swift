//
//  MessageBubble.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//
import SwiftUI

struct MessageBubble: View {
    let message: Message
    @State private var showingShareSheet = false
    @State private var shareContent: [Any] = []
    
    var body: some View {
        HStack(alignment: .top, spacing: 8) {
            if message.role == .user {
                Spacer()
            }
            
            // Avatar
            if message.role == .assistant {
                Circle()
                    .fill(Color.blue.opacity(0.1))
                    .frame(width: 32, height: 32)
                    .overlay(
                        Image(systemName: "sparkles")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(.blue)
                    )
            }
            
            VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 4) {
                // Main content bubble
                VStack(alignment: .leading, spacing: 0) {
                    // Main message content
                    Text(message.content)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                        .font(.body)
                    
                    // Display structured advice details if available for assistant messages
                    if message.role == .assistant, let advice = message.structuredAdvice {
                        Rectangle()
                            .fill(Color.gray.opacity(0.1))
                            .frame(height: 1)
                            .padding(.horizontal, 12)
                        
                        VStack(alignment: .leading, spacing: 12) {
                            // Confidence Score
                            if let confidence = advice.confidenceScore {
                                HStack(spacing: 6) {
                                    Image(systemName: "checkmark.seal.fill")
                                        .font(.caption)
                                        .foregroundColor(.blue)
                                    Text("Confidence: \(confidence, specifier: "%.1f")")
                                        .font(.caption.weight(.semibold))
                                        .foregroundColor(.secondary)
                                }
                            }
                            
                            // Reasoning
                            if let reasoning = advice.reasoning, !reasoning.isEmpty {
                                VStack(alignment: .leading, spacing: 4) {
                                    HStack(spacing: 6) {
                                        Image(systemName: "lightbulb.fill")
                                            .font(.caption)
                                            .foregroundColor(.orange)
                                        Text("Reasoning:")
                                            .font(.caption.weight(.semibold))
                                            .foregroundColor(.secondary)
                                    }
                                    Text(reasoning)
                                        .font(.caption)
                                        .foregroundColor(.primary)
                                        .fixedSize(horizontal: false, vertical: true)
                                }
                            }
                            
                            // Alternatives
                            if let alternatives = advice.alternatives, !alternatives.isEmpty {
                                VStack(alignment: .leading, spacing: 6) {
                                    HStack(spacing: 6) {
                                        Image(systemName: "arrow.right.circle.fill")
                                            .font(.caption)
                                            .foregroundColor(.green)
                                        Text("Alternatives:")
                                            .font(.caption.weight(.semibold))
                                            .foregroundColor(.secondary)
                                    }
                                    
                                    ForEach(alternatives, id: \.player) { alt in
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text("• \(alt.player)")
                                                .font(.caption.weight(.medium))
                                                .foregroundColor(.primary)
                                            if let reason = alt.reason, !reason.isEmpty {
                                                Text(reason)
                                                    .font(.caption2)
                                                    .foregroundColor(.secondary)
                                                    .padding(.leading, 12)
                                            }
                                        }
                                    }
                                }
                            }
                            
                            // Model Identifier
                            if let modelId = advice.modelIdentifier, !modelId.isEmpty {
                                HStack {
                                    Spacer()
                                    Text("Generated by \(modelId)")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                        .background(Color.gray.opacity(0.05))
                    }
                }
                .background(bubbleColor)
                .foregroundColor(textColor)
                .clipShape(RoundedRectangle(cornerRadius: 18))
                .shadow(color: .black.opacity(0.08), radius: 2, x: 0, y: 1)
                .onLongPressGesture {
                    prepareMessageShare()
                    showingShareSheet = true
                    
                    // Haptic feedback for long press
                    let impactFeedback = UIImpactFeedbackGenerator(style: .medium)
                    impactFeedback.impactOccurred()
                }
                
                // Timestamp
                Text(timeString)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .padding(.horizontal, message.role == .user ? 0 : 8)
            }
            
            // User avatar
            if message.role == .user {
                Circle()
                    .fill(Color.blue)
                    .frame(width: 32, height: 32)
                    .overlay(
                        Text("You")
                            .font(.system(size: 10, weight: .medium))
                            .foregroundColor(.white)
                    )
            } else {
                Spacer()
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 6)
        .sheet(isPresented: $showingShareSheet) {
            if !shareContent.isEmpty {
                ShareSheet(activityItems: shareContent)
            }
        }
    }
    
    private func prepareMessageShare() {
        let role = message.role == .user ? "You" : "Fantasy Genius"
        let timestamp = DateFormatter.localizedString(from: message.timestamp, dateStyle: .medium, timeStyle: .short)
        
        var messageText = "💬 Fantasy Genius Message\n"
        messageText += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        messageText += "👤 From: \(role)\n"
        messageText += "📅 Date: \(timestamp)\n\n"
        messageText += "💭 Message:\n\(message.content)\n\n"
        
        // Add structured advice if available
        if let advice = message.structuredAdvice {
            messageText += "🎯 Additional Details:\n"
            
            if let reasoning = advice.reasoning, !reasoning.isEmpty {
                messageText += "• Reasoning: \(reasoning)\n"
            }
            
            if let confidence = advice.confidenceScore {
                messageText += "• Confidence: \(String(format: "%.0f%%", confidence * 100))\n"
            }
            
            if let alternatives = advice.alternatives, !alternatives.isEmpty {
                messageText += "• Alternatives:\n"
                for alt in alternatives {
                    messageText += "  - \(alt.player)"
                    if let reason = alt.reason, !reason.isEmpty {
                        messageText += ": \(reason)"
                    }
                    messageText += "\n"
                }
            }
        }
        
        messageText += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        messageText += "Shared from Fantasy Genius iOS App"
        
        shareContent = [messageText]
    }
    
    private var bubbleColor: Color {
        switch message.role {
        case .user:
            return Color.blue
        case .assistant:
            return Color(.systemBackground)
        case .system:
            return Color.gray.opacity(0.1)
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

// MARK: - ShareSheet
struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]
    let applicationActivities: [UIActivity]?
    @Environment(\.dismiss) private var dismiss
    
    init(activityItems: [Any], applicationActivities: [UIActivity]? = nil) {
        self.activityItems = activityItems
        self.applicationActivities = applicationActivities
    }
    
    func makeUIViewController(context: UIViewControllerRepresentableContext<ShareSheet>) -> UIActivityViewController {
        let controller = UIActivityViewController(
            activityItems: activityItems,
            applicationActivities: applicationActivities
        )
        
        // Configure for iOS 18.4 standards and Apple HIG
        controller.modalPresentationStyle = .pageSheet
        
        // Configure the sheet presentation for iOS 15+
        if let sheet = controller.sheetPresentationController {
            sheet.detents = [.medium(), .large()]
            sheet.prefersGrabberVisible = true
            sheet.preferredCornerRadius = 16
        }
        
        // Exclude activities that don't make sense for message sharing
        controller.excludedActivityTypes = [
            .assignToContact,
            .openInIBooks,
            .markupAsPDF,
            .addToReadingList,
            .postToVimeo,
            .postToFlickr,
            .postToTencentWeibo,
            .postToWeibo
        ]
        
        // Add completion handler for better UX
        controller.completionWithItemsHandler = { activityType, completed, returnedItems, error in
            // Handle completion if needed
            if completed {
                // Optional: Add haptic feedback for successful share
                let impactFeedback = UIImpactFeedbackGenerator(style: .light)
                impactFeedback.impactOccurred()
            }
        }
        
        return controller
    }
    
    func updateUIViewController(_ uiViewController: UIActivityViewController, context: UIViewControllerRepresentableContext<ShareSheet>) {
        // No updates needed
    }
}

// Preview needs adjustment if Message init changed significantly for previews
struct MessageBubble_Previews: PreviewProvider {
    static var previews: some View {
        VStack {
            MessageBubble(message: Message(role: .user, content: "Hello AI!"))
            MessageBubble(message: Message(role: .assistant, content: "Hello User! This is my main advice."))
            MessageBubble(message: Message(role: .assistant, content: "Start Player X.", structuredAdvice: StructuredAdviceResponse(
                mainAdvice: "Start Player X.",
                reasoning: "Player X has a great matchup this week and has been performing consistently well. Player Y is facing a tough defense.",
                confidenceScore: 0.85,
                alternatives: [
                    AdviceAlternativePayload(player: "Player Y", reason: "If Player X is unexpectedly out."),
                    AdviceAlternativePayload(player: "Player Z", reason: "A risky high-upside play if you need it.")
                ],
                modelIdentifier: "gpt-4o-mini-preview_0720"
            )))
        }
        .padding()
    }
}
