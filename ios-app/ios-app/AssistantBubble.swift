//
//  AssistantBubble.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//

import SwiftUI

struct AssistantBubble: View {
    let message: Message
    @State private var showingDetailsOverlay = false
    @State private var showCopyConfirmation = false
    
    private var textColor: Color {
        if extractedAdvice == nil && message.content.count < 100 {
            return AppColors.primaryFontColor.opacity(0.8)
        }
        return AppColors.primaryFontColor
    }
    
    // Attempts to retrieve advice from either the parsed field or by decoding JSON in `message.content`
    private var extractedAdvice: StructuredAdviceResponse? {
        if let advice = message.structuredAdvice { return advice }
        return Self.decodeAdvice(from: message.content)
    }
    
    // Display text is either the structured advice's main point or the raw message
    private var displayText: String {
        return extractedAdvice?.mainAdvice
            ?? Self.extractMainAdvice(from: message.content)
            ?? message.content
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack(alignment: .bottom, spacing: 8) {
                VStack(alignment: .leading, spacing: 4) {
                    if !message.content.isEmpty {
                        textBubble()
                    }
                    
                    if !imageDataAttachments.isEmpty {
                        imageAttachmentsView()
                    }
                    
                    aiMessageControls
                }
                .textSelection(.enabled)
                .padding(.trailing, 40) // Indent bubble from screen edge
            }
            .overlay(copyConfirmationOverlay, alignment: .top)
        }
        .padding(.vertical, 5)
        .padding(.horizontal, 10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .sheet(isPresented: $showingDetailsOverlay) {
            if let advice = extractedAdvice {
                DetailsCardView(
                    advice: advice,
                    onDismiss: { showingDetailsOverlay = false },
                    onShare: { /* Implement share action for advice card */ }
                )
                .background(AppColors.backgroundColor.edgesIgnoringSafeArea(.all))
            }
        }
    }
    
    private func textBubble() -> some View {
        BubbleShell(corners: [.topRight, .bottomRight, .topLeft]) {
            Text(displayText)
                .font(.system(size: 16))
                .foregroundColor(textColor)
                .lineSpacing(3)
                .textSelection(.enabled)
        }
        .background(Color.clear)
        .shadow(color: Color.black.opacity(0.05), radius: 2, x: 1, y: 1)
    }
    
    private func imageAttachmentsView() -> some View {
        ForEach(imageDataAttachments, id: \.self) { imageData in
            if let uiImage = UIImage(data: imageData) {
                Image(uiImage: uiImage)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: 200, maxHeight: 200)
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                    .overlay(
                        RoundedRectangle(cornerRadius: 10)
                            .stroke(AppColors.primaryFontColor.opacity(0.2), lineWidth: 1)
                    )
                    .padding(.top, message.content.isEmpty ? 0 : 4) // Padding if there's text above
            }
        }
    }
    
    @ViewBuilder
    private var aiMessageControls: some View {
        HStack(alignment: .center, spacing: 10) {
            // Copy main advice
            Button {
                let textToCopy = extractedAdvice?.mainAdvice ?? Self.extractMainAdvice(from: message.content) ?? message.content
                UIPasteboard.general.string = textToCopy
                triggerCopyConfirmation()
            } label: {
                Image(systemName: "doc.on.doc.fill")
                    .font(.caption)
                    .foregroundColor(AppColors.primaryFontColor.opacity(0.7))
            }
            .buttonStyle(.plain)
            
            // Share main advice
            ShareLink(item: extractedAdvice?.mainAdvice ?? Self.extractMainAdvice(from: message.content) ?? message.content) {
                Image(systemName: "square.and.arrow.up")
                    .font(.caption)
                    .foregroundColor(AppColors.primaryFontColor.opacity(0.7))
            }
            
            // Make the "Thought for …s" label open the details pane
            if extractedAdvice != nil, let thoughtTime = thoughtTime {
                Button {
                    showingDetailsOverlay = true
                    UIImpactFeedbackGenerator(style: .light).impactOccurred()
                } label: {
                    Text(" Thought for \(thoughtTime)s")
                        .font(.caption2)
                        .italic()
                        .foregroundColor(AppColors.primaryFontColor.opacity(0.6))
                }
                .buttonStyle(.plain)
            }
            Spacer()
        }
        .padding(.top, 4)
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
                .background(AppColors.primaryFontColor.opacity(0.9))
                .foregroundColor(Color.white)
                .clipShape(Capsule())
                .transition(.opacity.combined(with: .scale(scale: 0.9)))
                .offset(y: -25) // Position above the bubble
                .zIndex(1) // Ensure it's on top
        }
    }
    
    private var thoughtTime: String? {
        let baseTime = 1.2
        let contentLength = Double(message.content.count)
        let hasStructuredAdvice = extractedAdvice != nil
        var time = baseTime + (contentLength / 100.0) * 0.8
        if hasStructuredAdvice { time += 1.5 }
        let randomFactor = Double.random(in: 0.8...1.3)
        time *= randomFactor
        time = max(1.0, min(12.0, time))
        return String(format: "%.1f", time)
    }
    
    // Compute raw image data from attachments
    private var imageDataAttachments: [Data] {
        message.attachments
            .filter { $0.type == .image }
            .compactMap { $0.data }
    }
    
    // Helper to decode advice JSON that may have been returned as a raw string
    private static func decodeAdvice(from content: String) -> StructuredAdviceResponse? {
        guard content.contains("\"main_advice\""),
              let data = content.data(using: .utf8) else { return nil }
        return try? JSONDecoder().decode(StructuredAdviceResponse.self, from: data)
    }
    
    /// Extracts the "main_advice" string from a raw JSON payload without requiring full decoding.
    private static func extractMainAdvice(from content: String) -> String? {
        guard let data = content.data(using: .utf8),
              let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let main = object["main_advice"] as? String else { return nil }
        return main
    }
} 