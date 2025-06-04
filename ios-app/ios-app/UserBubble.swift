//
//  UserBubble.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//

import SwiftUI

struct UserBubble: View {
    let message: Message
    @State private var showCopyConfirmation = false
    
    var body: some View {
        VStack(alignment: .trailing, spacing: 2) {
            HStack(alignment: .bottom, spacing: 0) {
                VStack(alignment: .trailing, spacing: 4) {
                    if !message.content.isEmpty {
                        textBubble()
                    }
                    
                    if !imageDataAttachments.isEmpty {
                        imageAttachmentsView()
                    }
                }
                .textSelection(.enabled)
                .padding(.leading, 40) // Indent bubble from screen edge
            }
            .overlay(copyConfirmationOverlay, alignment: .top)
        }
        .padding(.vertical, 5)
        .padding(.horizontal, 10)
        .frame(maxWidth: .infinity, alignment: .trailing)
    }
    
    private func textBubble() -> some View {
        BubbleShell(corners: [.topLeft, .bottomLeft, .topRight]) {
            Text(message.content)
                .font(.system(size: 16))
                .foregroundColor(.white)
                .lineSpacing(3)
                .textSelection(.enabled)
        }
        .background(AppColors.primaryFontColor)
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
                    .padding(.top, message.content.isEmpty ? 0 : 4)
            }
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
                .background(AppColors.primaryFontColor.opacity(0.9))
                .foregroundColor(Color.white)
                .clipShape(Capsule())
                .transition(.opacity.combined(with: .scale(scale: 0.9)))
                .offset(y: -25)
                .zIndex(1)
        }
    }
    
    // Compute raw image data from attachments
    private var imageDataAttachments: [Data] {
        message.attachments
            .filter { $0.type == .image }
            .compactMap { $0.data }
    }
} 