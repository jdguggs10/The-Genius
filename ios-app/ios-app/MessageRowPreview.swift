//
//  MessageRowPreview.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//

import SwiftUI

#Preview {
    VStack(spacing: 20) {
        // User message with text
        MessageRow(message: Message(
            id: UUID().uuidString,
            createdAt: Date(),
            role: .user,
            content: "This is a user message that's somewhat longer to test wrapping and bubble sizing.",
            attachments: []
        ))
        
        // Assistant message with structured advice
        let adviceJSON = """
        {
            "main_advice": "Start Cooper Kupp as your WR1 this week.",
            "reasoning": "Kupp is facing the 28th ranked pass defense and should see heavy target volume with the Rams likely playing from behind.",
            "confidence_score": 0.85,
            "alternatives": [
                {
                    "player": "Justin Jefferson",
                    "reason": "Also a strong play but has a tougher matchup against a top-5 pass defense."
                },
                {
                    "player": "Ja'Marr Chase",
                    "reason": "Good option but splitting targets with Tee Higgins limits ceiling."
                }
            ],
            "model_identifier": "Claude 3.5"
        }
        """
        
        let jsonData = adviceJSON.data(using: .utf8)!
        let advice = try! JSONDecoder().decode(StructuredAdviceResponse.self, from: jsonData)
        
        MessageRow(message: Message(
            id: UUID().uuidString,
            createdAt: Date(),
            role: .assistant,
            content: adviceJSON,
            attachments: [],
            structuredAdvice: advice
        ))
        
        // User message with image
        if let image = UIImage(named: "Image"), let imageData = image.jpegData(compressionQuality: 0.8) {
            MessageRow(message: Message(
                id: UUID().uuidString,
                createdAt: Date(),
                role: .user,
                content: "Check out this image",
                attachments: [Message.Attachment(type: .image, data: imageData)]
            ))
        }
    }
    .padding()
    .background(AppColors.backgroundColor)
} 