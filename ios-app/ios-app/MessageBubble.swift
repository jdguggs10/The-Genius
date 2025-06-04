//
//  MessageBubble.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//
import SwiftUI
import UIKit

private let appBackgroundColor = Color(red: 253/255, green: 245/255, blue: 230/255) // FDF5E6
private let appPrimaryFontColor = Color(red: 61/255, green: 108/255, blue: 104/255) // 3D6C68

struct MessageBubble: View {
    let message: Message
    @State private var showingDetailsOverlay = false
    @State private var showCopyConfirmation = false
    
    private var isUserMessage: Bool { message.role == .user }
    private var bubbleColor: Color {
        // For assistant messages that are purely informational (like errors or simple status), use a more subdued or clear background.
        if message.role == .assistant && message.structuredAdvice == nil && message.content.count < 100 { // Example condition
            return Color.clear // Or a very light appBackgroundColor shade
        }
        return isUserMessage ? appPrimaryFontColor : Color(.systemGray4) // SystemGray4 is a bit more visible than Gray5
    }
    private var textColor: Color {
        if message.role == .assistant && message.structuredAdvice == nil && message.content.count < 100 {
            return appPrimaryFontColor.opacity(0.8)
        }
        return isUserMessage ? Color.white : appPrimaryFontColor
    }
    private var alignment: Alignment {
        isUserMessage ? .trailing : .leading
    }
    /// Horizontal alignment helper for stack views
    private var horizontalAlignment: HorizontalAlignment {
        isUserMessage ? .trailing : .leading
    }
    private var horizontalPaddingFromEdge: Edge.Set {
        isUserMessage ? .leading : .trailing
    }

    // Compute raw image data from attachments
    private var imageDataAttachments: [Data] {
        message.attachments
            .filter { $0.type == .image }
            .compactMap { $0.data }
    }

    var body: some View {
        VStack(alignment: horizontalAlignment, spacing: 2) { // Changed HStack to VStack for timestamp placement
            messageContentWrapper
        }
        .padding(.vertical, 5)
        .padding(.horizontal, 10) // Universal horizontal padding for the whole bubble container
        .frame(maxWidth: .infinity, alignment: alignment)
        .sheet(isPresented: $showingDetailsOverlay) {
            if let advice = message.structuredAdvice {
                DetailsCardView(
                    advice: advice,
                    onDismiss: { showingDetailsOverlay = false },
                    onShare: { /* Implement share action for advice card */ }
                )
                .background(appBackgroundColor.edgesIgnoringSafeArea(.all))
            }
        }
    }
    
    @ViewBuilder
    private var messageContentWrapper: some View {
        let hasBubble = !(message.role == .assistant && message.structuredAdvice == nil && message.content.count < 100)
        let imageData = imageDataAttachments
        
        HStack(alignment: .bottom, spacing: isUserMessage ? 0 : 8) {
            // For user messages, the copy/share context menu is on the bubble
            // For assistant, they are explicit buttons below the text

            VStack(alignment: horizontalAlignment, spacing: 4) {
                if !message.content.isEmpty {
                    textBubble(hasBubble: hasBubble)
                }
                if !imageData.isEmpty {
                    imageAttachmentsView(imageData: imageData, hasBubble: hasBubble)
                }
                
                if message.role == .assistant {
                    aiMessageControls
                }
            }
            .padding(horizontalPaddingFromEdge, hasBubble ? 40 : 0) // Indent bubble from screen edge
        }
        .overlay(copyConfirmationOverlay, alignment: .top) // Position overlay relative to the whole bubble content
    }

    private func textBubble(hasBubble: Bool) -> some View {
        // Always show only the high‑level advice inside the bubble.
        let displayText = message.structuredAdvice?.mainAdvice ?? message.content
        
        return Text(displayText)
            .font(.system(size: 16))
            .foregroundColor(textColor)
            .lineSpacing(3)
            .padding(hasBubble ? EdgeInsets(top: 10, leading: 12, bottom: 10, trailing: 12) : EdgeInsets())
            .background(hasBubble ? bubbleColor : Color.clear)
            .clipShape(RoundedCorner(radius: 16, corners: determineCorners(hasBubble: hasBubble)))
            .shadow(color: hasBubble ? Color.black.opacity(0.05) : Color.clear, radius: 2, x: 1, y: 1)
            .contentShape(Rectangle())
            .contextMenu {
                if isUserMessage && hasBubble {
                    copyButton
                }
            }
    }
    
    private func imageAttachmentsView(imageData: [Data], hasBubble: Bool) -> some View {
        ForEach(imageData, id: \.self) { imageData in
            if let uiImage = UIImage(data: imageData) {
                Image(uiImage: uiImage)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: 200, maxHeight: 200)
                    .clipShape(RoundedRectangle(cornerRadius: hasBubble ? 10 : 0))
                    .overlay(
                        RoundedRectangle(cornerRadius: hasBubble ? 10 : 0)
                            .stroke(hasBubble ? appPrimaryFontColor.opacity(0.2) : Color.clear, lineWidth: 1)
                    )
                    .padding(.top, message.content.isEmpty ? 0 : 4) // Padding if there's text above
            }
        }
    }
    
    private func determineCorners(hasBubble: Bool) -> UIRectCorner {
        if !hasBubble { return [] }
        return isUserMessage ? [.topLeft, .bottomLeft, .topRight] : [.topRight, .bottomRight, .topLeft]
    }

    @ViewBuilder
    private var aiMessageControls: some View {
        HStack(alignment: .center, spacing: 10) {
            Button {
                // Copy the main advice text if structured advice exists, otherwise copy the content
                let textToCopy = message.structuredAdvice?.mainAdvice ?? message.content
                UIPasteboard.general.string = textToCopy
                triggerCopyConfirmation()
            } label: {
                Image(systemName: "doc.on.doc.fill")
                    .font(.caption)
                    .foregroundColor(appPrimaryFontColor.opacity(0.7))
            }
            .buttonStyle(.plain)

            ShareLink(item: message.structuredAdvice?.mainAdvice ?? message.content) {
                Image(systemName: "square.and.arrow.up")
                    .font(.caption)
                    .foregroundColor(appPrimaryFontColor.opacity(0.7))
            }

            // Make the “Thought for …s” label open the details pane
            if message.structuredAdvice != nil, let thoughtTime = thoughtTime {
                Button {
                    showingDetailsOverlay = true
                    UIImpactFeedbackGenerator(style: .light).impactOccurred()
                } label: {
                    Text(" Thought for \(thoughtTime)s")
                        .font(.caption2)
                        .italic()
                        .foregroundColor(appPrimaryFontColor.opacity(0.6))
                }
                .buttonStyle(.plain)
            }
            Spacer()
        }
        .padding(.top, 4)
    }
    
    private var copyButton: some View {
        Button {
            // Use the same logic for user messages
            let textToCopy = message.structuredAdvice?.mainAdvice ?? message.content
            UIPasteboard.general.string = textToCopy
            triggerCopyConfirmation()
        } label: {
            Label("Copy Text", systemImage: "doc.on.doc.fill")
        }
    }
    
    private func triggerCopyConfirmation() {
        withAnimation(.easeInOut(duration: 0.2)) {
            showCopyConfirmation = true
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            withAnimation(.easeInOut(duration: 0.3)) {
                showCopyConfirmation = false
            }
        }
    }

    @ViewBuilder
    private var copyConfirmationOverlay: some View {
        if showCopyConfirmation {
            Text("Copied!")
                .font(.caption)
                .padding(.vertical, 6)
                .padding(.horizontal, 10)
                .background(appPrimaryFontColor.opacity(0.9))
                .foregroundColor(Color.white)
                .clipShape(Capsule())
                .transition(.opacity.combined(with: .scale(scale: 0.9)))
                .offset(y: -25) // Position above the bubble
                .zIndex(1) // Ensure it's on top
        }
    }

    private var thoughtTime: String? {
        guard message.role == .assistant else { return nil }
        let baseTime = 1.2
        let contentLength = Double(message.content.count)
        let hasStructuredAdvice = message.structuredAdvice != nil
        var time = baseTime + (contentLength / 100.0) * 0.8
        if hasStructuredAdvice { time += 1.5 }
        let randomFactor = Double.random(in: 0.8...1.3)
        time *= randomFactor
        time = max(1.0, min(12.0, time))
        return String(format: "%.1f", time)
    }
}

// Custom RoundedCorner shape for message bubbles
struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: radius, height: radius))
        return Path(path.cgPath)
    }
}

// MARK: - Details Card View
struct DetailsCardView: View {
    let advice: StructuredAdviceResponse
    let onDismiss: () -> Void
    let onShare: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            Divider().background(appPrimaryFontColor.opacity(0.2))
            content
        }
        .background(appBackgroundColor.edgesIgnoringSafeArea(.all)) // Main background
    }
    
    private var header: some View {
        HStack {
            Text("Details")
                .font(.title2.weight(.semibold))
                .foregroundColor(appPrimaryFontColor)
            Spacer()
            Button(action: onDismiss) {
                Image(systemName: "xmark.circle.fill") // Changed to filled version
                    .font(.title2)
                    .foregroundColor(appPrimaryFontColor.opacity(0.7))
            }
            .buttonStyle(.plain)
        }
        .padding()
    }
    
    private var content: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Main advice
                detailSection(title: "Advice", icon: "text.bubble.fill", textBlock: advice.mainAdvice, tint: appPrimaryFontColor)
                
                // Reasoning (if available)
                if let reasoning = advice.reasoning {
                    detailSection(title: "Reasoning", icon: "brain.fill", textBlock: reasoning, tint: appPrimaryFontColor.opacity(0.8))
                }
                
                // Confidence score (if available)
                if let confidence = advice.confidenceScore {
                    detailSection(title: "Confidence Score", icon: "checkmark.seal.fill", value: String(format: "%.0f%%", confidence * 100), tint: appPrimaryFontColor)
                }
                
                // Alternatives (if available)
                if let alternatives = advice.alternatives, !alternatives.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(spacing: 8) {
                            Image(systemName: "arrow.triangle.branch")
                                .font(.headline)
                                .foregroundColor(appPrimaryFontColor.opacity(0.7))
                            Text("Alternatives")
                                .font(.headline)
                                .foregroundColor(appPrimaryFontColor)
                        }
                        
                        ForEach(alternatives, id: \.player) { alternative in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(alternative.player)
                                    .font(.subheadline.weight(.medium))
                                    .foregroundColor(appPrimaryFontColor)
                                if let reason = alternative.reason {
                                    Text(reason)
                                        .font(.caption)
                                        .foregroundColor(appPrimaryFontColor.opacity(0.8))
                                }
                            }
                            .padding(.vertical, 6)
                            .padding(.horizontal, 10)
                            .background(appPrimaryFontColor.opacity(0.05))
                            .cornerRadius(8)
                            .padding(.leading, 28)
                        }
                    }
                }
                
                // Model identifier (if available)
                if let modelId = advice.modelIdentifier {
                    detailSection(title: "Model", icon: "cpu", value: modelId, tint: appPrimaryFontColor.opacity(0.6))
                }
            }
            .padding()
        }
    }
    
    @ViewBuilder
    private func detailSection(title: String, icon: String, value: String? = nil, textBlock: String? = nil, tint: Color) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.headline)
                    .foregroundColor(tint)
                Text(title)
                    .font(.headline)
                    .foregroundColor(appPrimaryFontColor)
            }
            if let value = value {
                Text(value)
                    .font(.body)
                    .foregroundColor(appPrimaryFontColor.opacity(0.9))
                    .padding(.leading, 28) // Indent under icon
            }
            if let textBlock = textBlock {
                Text(textBlock)
                    .font(.body)
                    .foregroundColor(appPrimaryFontColor.opacity(0.9))
                    .padding(.leading, 28) // Indent under icon
                    .lineSpacing(3)
            }
        }
    }
}
