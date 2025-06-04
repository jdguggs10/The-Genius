//
//  DetailsCardView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//

import SwiftUI

struct DetailsCardView: View {
    let advice: StructuredAdviceResponse
    let onDismiss: () -> Void
    let onShare: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            Divider().background(AppColors.primaryFontColor.opacity(0.2))
            content
        }
        .background(AppColors.backgroundColor.edgesIgnoringSafeArea(.all)) // Main background
    }
    
    private var header: some View {
        HStack {
            Text("Details")
                .font(.title2.weight(.semibold))
                .foregroundColor(AppColors.primaryFontColor)
            Spacer()
            Button(action: onDismiss) {
                Image(systemName: "xmark.circle.fill") // Changed to filled version
                    .font(.title2)
                    .foregroundColor(AppColors.primaryFontColor.opacity(0.7))
            }
            .buttonStyle(.plain)
        }
        .padding()
    }
    
    private var content: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Main advice
                detailSection(title: "Advice", icon: "text.bubble.fill", textBlock: advice.mainAdvice, tint: AppColors.primaryFontColor)
                
                // Reasoning (if available)
                if let reasoning = advice.reasoning {
                    detailSection(title: "Reasoning", icon: "brain.fill", textBlock: reasoning, tint: AppColors.primaryFontColor.opacity(0.8))
                }
                
                // Confidence score (if available)
                if let confidence = advice.confidenceScore {
                    detailSection(title: "Confidence Score", icon: "checkmark.seal.fill", value: String(format: "%.0f%%", confidence * 100), tint: AppColors.primaryFontColor)
                }
                
                // Alternatives (if available)
                if let alternatives = advice.alternatives, !alternatives.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack(spacing: 8) {
                            Image(systemName: "arrow.triangle.branch")
                                .font(.headline)
                                .foregroundColor(AppColors.primaryFontColor.opacity(0.7))
                            Text("Alternatives")
                                .font(.headline)
                                .foregroundColor(AppColors.primaryFontColor)
                        }
                        
                        ForEach(alternatives, id: \.player) { alternative in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(alternative.player)
                                    .font(.subheadline.weight(.medium))
                                    .foregroundColor(AppColors.primaryFontColor)
                                if let reason = alternative.reason {
                                    Text(reason)
                                        .font(.caption)
                                        .foregroundColor(AppColors.primaryFontColor.opacity(0.8))
                                }
                            }
                            .padding(.vertical, 6)
                            .padding(.horizontal, 10)
                            .background(AppColors.primaryFontColor.opacity(0.05))
                            .cornerRadius(8)
                            .padding(.leading, 28)
                        }
                    }
                }
                
                // Model identifier (if available)
                if let modelId = advice.modelIdentifier {
                    detailSection(title: "Model", icon: "cpu", value: modelId, tint: AppColors.primaryFontColor.opacity(0.6))
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
                    .foregroundColor(AppColors.primaryFontColor)
            }
            if let value = value {
                Text(value)
                    .font(.body)
                    .foregroundColor(AppColors.primaryFontColor.opacity(0.9))
                    .padding(.leading, 28) // Indent under icon
            }
            if let textBlock = textBlock {
                Text(textBlock)
                    .font(.body)
                    .foregroundColor(AppColors.primaryFontColor.opacity(0.9))
                    .padding(.leading, 28) // Indent under icon
                    .lineSpacing(3)
            }
        }
    }
} 