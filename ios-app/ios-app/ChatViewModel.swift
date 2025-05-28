//
//  ChatViewModel.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/28/25.
//
import Foundation
import SwiftUI

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [Message] = []
    @Published var currentInput: String = ""
    @Published var isLoading: Bool = false
    @Published var draftAttachmentData: [Data] = []
    
    // Use your backend URL - change this to match your deployment
    private let backendURL = "https://genius-backend-nhl3.onrender.com/advice"
    // For local testing, use: "http://localhost:8000/advice"
    
    // Send a message
    func sendMessage() {
        // Make sure there's text to send or attachments to send
        let trimmedInput = currentInput.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedInput.isEmpty || !draftAttachmentData.isEmpty else { return }
        
        // Create attachments from draft data
        let attachments = draftAttachmentData.map { data in
            ChatAttachment(type: .image, data: data) // Assuming all drafts are images for now
        }
        
        // Create user message
        let userMessage = Message(
            role: .user,
            content: trimmedInput, // Use trimmed input
            attachments: attachments
        )
        
        // Add to messages
        messages.append(userMessage)
        
        // Clear input
        currentInput = ""
        draftAttachmentData.removeAll()
        
        // Start getting AI response
        Task {
            await getAIResponse(for: trimmedInput)
        }
    }
    
    // Get response from your backend
    private func getAIResponse(for prompt: String) async {
        isLoading = true
        
        // Create empty assistant message that we'll update
        let assistantMessage = Message(role: .assistant, content: "")
        messages.append(assistantMessage)
        let messageIndex = messages.count - 1
        
        // Prepare the request to your backend
        guard let url = URL(string: backendURL) else {
            messages[messageIndex].content = "Error: Invalid backend URL"
            isLoading = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Build the conversation array for your backend
        let conversation = messages.dropLast().map { message in
            ["role": message.role.rawValue, "content": message.content]
        }
        
        let body: [String: Any] = [
            "conversation": conversation + [["role": "user", "content": prompt]],
            "enable_web_search": false,
            "model": "gpt-4.1"  // Request GPT-4.1 specifically
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
            
            // Make the request
            let (data, response) = try await URLSession.shared.data(for: request)
            
            // Check response status
            if let httpResponse = response as? HTTPURLResponse,
               httpResponse.statusCode != 200 {
                messages[messageIndex].content = "Error: Server returned status \(httpResponse.statusCode)"
                isLoading = false
                return
            }
            
            // Parse the response
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let reply = json["reply"] as? String {
                // Update the message with the full response
                messages[messageIndex].content = reply
            } else {
                messages[messageIndex].content = "Error: Could not parse response"
            }
            
        } catch {
            // Handle error
            messages[messageIndex].content = "Sorry, I encountered an error: \(error.localizedDescription)"
        }
        
        isLoading = false
        saveConversation()
    }
    
    // Save conversation to storage
    func saveConversation() {
        if let encoded = try? JSONEncoder().encode(messages) {
            UserDefaults.standard.set(encoded, forKey: "current_conversation")
        }
    }
    
    // Load conversation from storage
    func loadConversation() {
        if let data = UserDefaults.standard.data(forKey: "current_conversation"),
           let decoded = try? JSONDecoder().decode([Message].self, from: data) {
            messages = decoded
        }
    }
}
