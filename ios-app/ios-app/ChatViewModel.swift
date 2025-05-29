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
    @Published var isSearching: Bool = false
    @Published var streamingText: String = ""
    @Published var statusMessage: String? = nil
    @Published var draftAttachmentData: [Data] = []
    
    // No longer need latestStructuredAdvice here, it will be in the Message struct
    // @Published var latestStructuredAdvice: StructuredAdviceResponse? = nil 
    @Published var currentErrorMessage: String? = nil
    
    // Reference to conversation manager
    var conversationManager: ConversationManager?
    var currentConversationId: UUID?
    
    // Use your backend URL - change this to match your deployment
    private let backendURLString = "https://genius-backend-nhl3.onrender.com/advice" // Updated to Render URL
    
    // MARK: - Network Configuration
    private lazy var streamingSession: URLSession = {
        let config = URLSessionConfiguration.default
        // Increased timeouts for streaming
        config.timeoutIntervalForRequest = 60 // 1 minute for initial connection
        config.timeoutIntervalForResource = 600 // 10 minutes for complete resource
        config.requestCachePolicy = .reloadIgnoringLocalAndRemoteCacheData
        
        // Optimize for streaming
        config.httpMaximumConnectionsPerHost = 1
        config.httpShouldSetCookies = false
        config.httpCookieAcceptPolicy = .never
        
        // Network service type for real-time
        config.networkServiceType = .responsiveData
        
        return URLSession(configuration: config)
    }()
    
    func setConversationManager(_ manager: ConversationManager) {
        self.conversationManager = manager
    }
    
    // Force UI update method to ensure SwiftUI detects changes
    private func forceUIUpdate() {
        DispatchQueue.main.async { [weak self] in
            self?.objectWillChange.send()
        }
    }
    
    func loadConversation(for conversationId: UUID?) {
        guard let manager = conversationManager else { return }
        
        if let conversationId = conversationId,
           let conversation = manager.conversations.first(where: { $0.id == conversationId }) {
            self.currentConversationId = conversationId
            self.messages = conversation.messages
        } else if let firstConversation = manager.conversations.first {
            self.currentConversationId = firstConversation.id
            self.messages = firstConversation.messages
        } else {
            // Create a new conversation if none exist
            let newConversation = manager.createNewConversation()
            self.currentConversationId = newConversation.id
            self.messages = [
                Message(role: .assistant, content: "Welcome to Fantasy Genius! How can I help you today?")
            ]
        }
        
        currentErrorMessage = nil
    }
    
    // Send a message
    func sendMessage() {
        let trimmedInput = currentInput.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedInput.isEmpty || !draftAttachmentData.isEmpty else { return }
        
        let attachments = draftAttachmentData.map { data in
            ChatAttachment(type: .image, data: data) // Assuming images for now
        }
        
        let userMessage = Message(
            role: .user,
            content: trimmedInput,
            attachments: attachments
        )
        
        messages.append(userMessage)
        currentInput = ""
        draftAttachmentData.removeAll()
        currentErrorMessage = nil // Clear previous errors
        
        // Update the conversation in the manager
        updateCurrentConversation()
        
        Task {
            await fetchStreamingStructuredAdvice()
        }
    }
    
    private func updateCurrentConversation() {
        guard let manager = conversationManager,
              let conversationId = currentConversationId,
              var conversation = manager.conversations.first(where: { $0.id == conversationId }) else {
            return
        }
        
        conversation.messages = messages
        conversation.updateLastMessageDate()
        
        // Auto-generate title from first user message if it's still "New Chat"
        if conversation.title == "New Chat" {
            conversation.updateTitleFromFirstMessage()
        }
        
        manager.updateConversation(conversation)
    }
    
    private func fetchStreamingStructuredAdvice() async {
        isLoading = true
        isSearching = false
        streamingText = ""
        statusMessage = nil
        currentErrorMessage = nil
        
        let assistantMessagePlaceholder = Message(role: .assistant, content: "")
        messages.append(assistantMessagePlaceholder)
        
        guard let assistantMessageIndex = messages.lastIndex(where: { $0.id == assistantMessagePlaceholder.id }) else {
            currentErrorMessage = "Internal error: Could not find placeholder message."
            isLoading = false
            return
        }

        guard let url = URL(string: backendURLString) else {
            messages[assistantMessageIndex].content = "Error: Invalid backend URL configured."
            currentErrorMessage = "Error: Invalid backend URL configured."
            isLoading = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("text/event-stream", forHTTPHeaderField: "Accept")
        request.setValue("no-cache", forHTTPHeaderField: "Cache-Control")
        request.setValue("keep-alive", forHTTPHeaderField: "Connection")
        
        // Prepare the conversation payload
        let conversationPayloads = self.messages.filter { $0.id != assistantMessagePlaceholder.id }.map {
            MessagePayload(role: $0.role, content: $0.content)
        }
        let adviceRequest = AdviceRequestPayload(conversation: conversationPayloads)

        do {
            request.httpBody = try JSONEncoder().encode(adviceRequest)
        } catch {
            messages[assistantMessageIndex].content = "Error: Could not encode request: \(error.localizedDescription)"
            currentErrorMessage = "Error: Could not encode request: \(error.localizedDescription)"
            isLoading = false
            return
        }
        
        // Use the streaming session with proper configuration
        do {
            let (asyncBytes, response) = try await streamingSession.bytes(for: request)
            
            // Check HTTP response
            if let httpResponse = response as? HTTPURLResponse {
                if httpResponse.statusCode != 200 {
                    let errorMsg = "HTTP Error: \(httpResponse.statusCode)"
                    messages[assistantMessageIndex].content = errorMsg
                    currentErrorMessage = errorMsg
                    isLoading = false
                    return
                }
            }
            
            var accumulatedText = ""
            var eventCount = 0
            var lineCount = 0
            var currentEventType: String? = nil
            var currentData: String? = nil
            
            for try await line in asyncBytes.lines {
                lineCount += 1
                
                if line.hasPrefix("event: ") {
                    // Process previous event if we have both type and data
                    if let eventType = currentEventType, let data = currentData {
                        eventCount += 1
                        await processSSEEvent(eventType: eventType, data: data, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
                    }
                    
                    // Start new event
                    currentEventType = String(line.dropFirst(7)).trimmingCharacters(in: .whitespacesAndNewlines)
                    currentData = nil
                } else if line.hasPrefix("data: ") {
                    currentData = String(line.dropFirst(6))
                } else if line.isEmpty {
                    // Empty line - process current event if we have both type and data
                    if let eventType = currentEventType, let data = currentData {
                        eventCount += 1
                        await processSSEEvent(eventType: eventType, data: data, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
                        
                        // Reset for next event
                        currentEventType = nil
                        currentData = nil
                    }
                }
            }
            
            // Process final event if exists
            if let eventType = currentEventType, let data = currentData {
                await processSSEEvent(eventType: eventType, data: data, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
            }
            
            // Handle any remaining content
            if !accumulatedText.isEmpty && messages[assistantMessageIndex].content.isEmpty {
                messages[assistantMessageIndex].content = accumulatedText
            }
            
        } catch {
            let errorMsg = "Network error: \(error.localizedDescription)"
            messages[assistantMessageIndex].content = errorMsg
            currentErrorMessage = errorMsg
        }
        
        isLoading = false
        isSearching = false
        streamingText = ""
        statusMessage = nil
        saveConversation()
    }
    
    private func processSSEEvent(eventType: String, data: String, messageIndex: Int, accumulatedText: inout String) async {
        // Handle different event types
        if eventType == "status_update" {
            do {
                if let jsonData = data.data(using: .utf8),
                   let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                   let message = parsed["message"] as? String {
                    await MainActor.run {
                        statusMessage = message
                        if let status = parsed["status"] as? String {
                            isSearching = (status == "web_search_searching" || status == "web_search_started")
                        }
                    }
                }
            } catch {
                // Failed to parse status update - silently continue
            }
        } else if eventType == "text_delta" {
            do {
                if let jsonData = data.data(using: .utf8),
                   let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                   let delta = parsed["delta"] as? String {
                    accumulatedText += delta
                    
                    // Ensure UI updates happen on main thread with proper SwiftUI change detection
                    await MainActor.run {
                        // Create a new message instance to ensure SwiftUI detects the change
                        var updatedMessage = messages[messageIndex]
                        updatedMessage.content = accumulatedText
                        
                        // Signal change before updating
                        objectWillChange.send()
                        messages[messageIndex] = updatedMessage
                        
                        statusMessage = nil
                        isSearching = false
                        
                        // Force UI update to ensure real-time display
                        forceUIUpdate()
                    }
                }
            } catch {
                // Failed to parse text delta - silently continue
            }
        } else if eventType == "response_complete" {
            do {
                if let jsonData = data.data(using: .utf8),
                   let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                   let finalJson = parsed["final_json"] as? [String: Any] {
                    
                    let mainAdvice = finalJson["main_advice"] as? String ?? accumulatedText
                    let reasoning = finalJson["reasoning"] as? String
                    let confidence = finalJson["confidence_score"] as? Double
                    let modelId = finalJson["model_identifier"] as? String
                    
                    // Parse alternatives array
                    var alternatives: [AdviceAlternativePayload] = []
                    if let alternativesArray = finalJson["alternatives"] as? [[String: Any]] {
                        alternatives = alternativesArray.compactMap { altDict -> AdviceAlternativePayload? in
                            guard let player = altDict["player"] as? String else { return nil }
                            let reason = altDict["reason"] as? String
                            return AdviceAlternativePayload(player: player, reason: reason)
                        }
                    }
                    
                    // Use global NetworkModels.StructuredAdviceResponse with camelCase properties
                    let structuredAdvice = StructuredAdviceResponse(
                        mainAdvice: mainAdvice,
                        reasoning: reasoning,
                        confidenceScore: confidence,
                        alternatives: alternatives,
                        modelIdentifier: modelId
                    )
                    
                    // Ensure UI updates happen on main thread with explicit update
                    await MainActor.run {
                        var updatedMessage = messages[messageIndex]
                        updatedMessage.content = mainAdvice
                        updatedMessage.structuredAdvice = structuredAdvice
                        
                        // Signal change before updating
                        objectWillChange.send()
                        messages[messageIndex] = updatedMessage
                        
                        statusMessage = nil
                        isSearching = false
                        
                        // Force UI update to ensure real-time display
                        forceUIUpdate()
                    }
                }
            } catch {
                // Failed to parse response complete - silently continue
            }
        } else if eventType == "error" {
            do {
                if let jsonData = data.data(using: .utf8),
                   let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                   let errorMessage = parsed["message"] as? String {
                    await MainActor.run {
                        var updatedMessage = messages[messageIndex]
                        updatedMessage.content = "Error: \(errorMessage)"
                        messages[messageIndex] = updatedMessage
                        currentErrorMessage = "Error: \(errorMessage)"
                    }
                }
            } catch {
                // Failed to parse error - silently continue
            }
        }
        // Note: Unhandled event types are silently ignored
    }
    
    func saveConversation() {
        updateCurrentConversation()
    }
}
