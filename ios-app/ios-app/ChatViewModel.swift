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
    @Published private(set) var messages: [Message] = []
    @Published private(set) var isLoading: Bool = false
    @Published private(set) var isSearching: Bool = false
    @Published private(set) var streamingText: String = ""
    @Published private(set) var statusMessage: String? = nil
    @Published var draftAttachmentData: [Data] = []
    
    // No longer need latestStructuredAdvice here, it will be in the Message struct
    // @Published var latestStructuredAdvice: StructuredAdviceResponse? = nil 
    @Published private(set) var currentErrorMessage: String? = nil
    
    // Reference to conversation manager
    var conversationManager: ConversationManager?
    var currentConversationId: UUID?
    
    // Default model configuration - synced with backend
    private let defaultModel = "gpt-4.1-mini" // Matches backend OPENAI_DEFAULT_MODEL
    
    // MARK: - Message Windowing for Performance
    private let maxVisibleMessages = 1000 // Maximum messages to keep in memory
    private let messageBuffer = 50 // Buffer of additional messages to keep
    private var allMessages: [Message] = [] // Complete conversation history
    
    /// Computed property that returns windowed messages for display
    var displayMessages: [Message] {
        // For conversations under the limit, return all messages
        guard allMessages.count > maxVisibleMessages else {
            return allMessages
        }
        
        // For large conversations, return the most recent messages plus buffer
        let startIndex = max(0, allMessages.count - maxVisibleMessages)
        return Array(allMessages[startIndex...])
    }
    
    // Use ApiConfiguration for backend URL management
    private var backendURLString: String {
        return ApiConfiguration.getAdviceURL()
    }
    
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
    
    // MARK: - Model Configuration
    
    /// Fetch the backend's current default model
    func fetchBackendDefaultModel() async -> String? {
        guard let url = URL(string: ApiConfiguration.getModelURL()) else {
            return nil
        }
        
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let model = json["model"] as? String {
                return model
            }
        } catch {
            print("Failed to fetch backend default model: \(error)")
        }
        
        return nil
    }
    
    /// Get the model to use for requests (fetches from backend or uses fallback)
    private func getModelToUse() async -> String {
        if let backendModel = await fetchBackendDefaultModel() {
            return backendModel
        }
        return defaultModel // Fallback to hardcoded default
    }
    
    func setConversationManager(_ manager: ConversationManager) {
        self.conversationManager = manager
    }
    
    func loadConversation(for conversationId: UUID?) {
        guard let manager = conversationManager else { return }
        
        if let conversationId = conversationId,
           let conversation = manager.conversations.first(where: { $0.id == conversationId }) {
            self.currentConversationId = conversationId
            // Load all messages into internal storage
            self.allMessages = conversation.messages
            // Update the published messages with windowed display
            self.messages = displayMessages
        } else if let firstConversation = manager.conversations.first {
            self.currentConversationId = firstConversation.id
            self.allMessages = firstConversation.messages
            self.messages = displayMessages
        } else {
            // Create a new conversation if none exist
            let newConversation = manager.createNewConversation()
            self.currentConversationId = newConversation.id
            let welcomeMessage = Message(role: .assistant, content: "Welcome to Fantasy Genius! How can I help you today?")
            self.allMessages = [welcomeMessage]
            self.messages = displayMessages
        }
        
        currentErrorMessage = nil
    }
    
    // Send a message
    func sendMessage(_ messageText: String) {
        // Log API configuration for debugging
        ApiConfiguration.logConfiguration()
        
        let trimmedInput = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedInput.isEmpty || !draftAttachmentData.isEmpty else { return }
        
        let attachments = draftAttachmentData.map { data in
            ChatAttachment(type: .image, data: data) // Assuming images for now
        }
        
        let userMessage = Message(
            role: .user,
            content: trimmedInput,
            attachments: attachments
        )
        
        // Add to complete message history
        allMessages.append(userMessage)
        // Update displayed messages with windowing
        messages = displayMessages
        
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
        
        // Save the complete message history, not just the windowed display
        conversation.messages = allMessages
        conversation.updateLastMessageDate()
        
        // Auto-generate title from first user message if it's still "New Chat"
        if conversation.title == "New Chat" {
            conversation.updateTitleFromFirstMessage()
        }
        
        manager.updateConversation(conversation)
    }
    
    private func fetchStreamingStructuredAdvice() async {
        // Measure the entire operation for hang detection
        await HangDetector.shared.measureAsyncOperation(
            operation: {
                await performStreamingRequest()
            },
            description: "Streaming advice request"
        )
    }
    
    private func performStreamingRequest() async {
        setLoadingState(true)
        streamingText = ""
        statusMessage = nil
        currentErrorMessage = nil
        
        let assistantMessagePlaceholder = Message(role: .assistant, content: "")
        
        // Add to both allMessages and displayed messages with windowing
        allMessages.append(assistantMessagePlaceholder)
        messages = displayMessages
        
        // Find the placeholder in the displayed messages (not allMessages)
        guard let assistantMessageIndex = messages.lastIndex(where: { $0.id == assistantMessagePlaceholder.id }) else {
            setError("Internal error: Could not find placeholder message.")
            return
        }

        guard let url = URL(string: backendURLString) else {
            // Update both the displayed message and allMessages
            if let allMessageIndex = allMessages.lastIndex(where: { $0.id == assistantMessagePlaceholder.id }) {
                allMessages[allMessageIndex].content = "Error: Invalid backend URL configured."
            }
            messages[assistantMessageIndex].content = "Error: Invalid backend URL configured."
            setError("Error: Invalid backend URL configured.")
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("text/event-stream", forHTTPHeaderField: "Accept")
        request.setValue("no-cache", forHTTPHeaderField: "Cache-Control")
        request.setValue("keep-alive", forHTTPHeaderField: "Connection")
        
        // Get the current conversation to check for last response ID
        guard let manager = conversationManager,
              let conversationId = currentConversationId,
              var conversation = manager.conversations.first(where: { $0.id == conversationId }) else {
            currentErrorMessage = "Error: Could not find current conversation."
            isLoading = false
            return
        }
        
        // Get the latest user message (excluding the placeholder assistant message)
        guard let latestUserMessage = messages.dropLast().last(where: { $0.role == .user }) else {
            currentErrorMessage = "Error: No user message found."
            isLoading = false
            return
        }
        
        // Get the model to use
        let modelToUse = await getModelToUse()
        
        // Prepare the request payload using proper Responses API patterns
        let adviceRequest: AdviceRequestPayload
        
        if let lastResponseId = conversation.lastResponseId {
            // Continue conversation using previous_response_id (preferred approach)
            adviceRequest = AdviceRequestPayload(
                userMessage: latestUserMessage.content,
                previousResponseId: lastResponseId,
                model: modelToUse, // Use dynamically fetched model or fallback
                enableWebSearch: true
            )
        } else {
            // Start new conversation with full history
            let conversationPayloads = self.messages.filter { $0.id != assistantMessagePlaceholder.id }.map {
                MessagePayload(role: $0.role, content: $0.content)
            }
            adviceRequest = AdviceRequestPayload(
                conversation: conversationPayloads,
                model: modelToUse, // Use dynamically fetched model or fallback
                enableWebSearch: true
            )
        }

        do {
            request.httpBody = try JSONEncoder().encode(adviceRequest)
        } catch {
            messages[assistantMessageIndex].content = "Error: Could not encode request: \(error.localizedDescription)"
            setError("Error: Could not encode request: \(error.localizedDescription)")
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
                    setError(errorMsg)
                    return
                }
            }
            
            var accumulatedText = ""
            var responseId: String? = nil
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
                        let extractedResponseId = await processSSEEvent(eventType: eventType, data: data, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
                        if let extractedId = extractedResponseId {
                            responseId = extractedId
                        }
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
                        let extractedResponseId = await processSSEEvent(eventType: eventType, data: data, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
                        if let extractedId = extractedResponseId {
                            responseId = extractedId
                        }
                        
                        // Reset for next event
                        currentEventType = nil
                        currentData = nil
                    }
                }
            }
            
            // Process final event if exists
            if let eventType = currentEventType, let data = currentData {
                let extractedResponseId = await processSSEEvent(eventType: eventType, data: data, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
                if let extractedId = extractedResponseId {
                    responseId = extractedId
                }
            }
            
            // Handle any remaining content
            if !accumulatedText.isEmpty && messages[assistantMessageIndex].content.isEmpty {
                messages[assistantMessageIndex].content = accumulatedText
            }
            
            // Update conversation with the new response ID for future context
            if let responseId = responseId {
                conversation.updateLastResponseId(responseId)
                manager.updateConversation(conversation)
            }
            
        } catch {
            let errorMsg = "Network error: \(error.localizedDescription)"
            messages[assistantMessageIndex].content = errorMsg
            setError(errorMsg)
        }
        
        setLoadingState(false)
        streamingText = ""
        saveConversation()
    }
    
    // MARK: - Async JSON Parsing Functions
    
    /// Parse status update JSON data asynchronously
    private func parseStatusUpdate(_ data: String) async -> (message: String, status: String?)? {
        guard let jsonData = data.data(using: .utf8) else { return nil }
        
        do {
            guard let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                  let message = parsed["message"] as? String else { return nil }
            
            let status = parsed["status"] as? String
            return (message: message, status: status)
        } catch {
            return nil
        }
    }
    
    /// Parse text delta JSON data asynchronously
    private func parseTextDelta(_ data: String) async -> String? {
        guard let jsonData = data.data(using: .utf8) else { return nil }
        
        do {
            guard let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                  let delta = parsed["delta"] as? String else { return nil }
            
            return delta
        } catch {
            return nil
        }
    }
    
    /// Parse response complete JSON data asynchronously
    private func parseResponseComplete(_ data: String, accumulatedText: String) async -> (advice: StructuredAdviceResponse, responseId: String?)? {
        guard let jsonData = data.data(using: .utf8) else { return nil }
        
        do {
            guard let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                  let finalJson = parsed["final_json"] as? [String: Any] else { return nil }
            
            let mainAdvice = finalJson["main_advice"] as? String ?? accumulatedText
            let reasoning = finalJson["reasoning"] as? String
            let confidence = finalJson["confidence_score"] as? Double
            let modelId = finalJson["model_identifier"] as? String
            let responseId = finalJson["response_id"] as? String
            
            // Parse alternatives array
            var alternatives: [AdviceAlternativePayload] = []
            if let alternativesArray = finalJson["alternatives"] as? [[String: Any]] {
                alternatives = alternativesArray.compactMap { altDict -> AdviceAlternativePayload? in
                    guard let player = altDict["player"] as? String else { return nil }
                    let reason = altDict["reason"] as? String
                    return AdviceAlternativePayload(player: player, reason: reason)
                }
            }
            
            let structuredAdvice = StructuredAdviceResponse(
                mainAdvice: mainAdvice,
                reasoning: reasoning,
                confidenceScore: confidence,
                alternatives: alternatives,
                modelIdentifier: modelId,
                responseId: responseId
            )
            
            return (advice: structuredAdvice, responseId: responseId)
        } catch {
            return nil
        }
    }
    
    /// Parse error JSON data asynchronously
    private func parseError(_ data: String) async -> String? {
        guard let jsonData = data.data(using: .utf8) else { return nil }
        
        do {
            guard let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                  let errorMessage = parsed["message"] as? String else { return nil }
            
            return errorMessage
        } catch {
            return nil
        }
    }
    
    /// Parse response created JSON data asynchronously
    private func parseResponseCreated(_ data: String) async -> String? {
        guard let jsonData = data.data(using: .utf8) else { return nil }
        
        do {
            guard let parsed = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                  let responseId = parsed["response_id"] as? String else { return nil }
            
            return responseId
        } catch {
            return nil
        }
    }

    private func processSSEEvent(eventType: String, data: String, messageIndex: Int, accumulatedText: inout String) async -> String? {
        // Handle different event types based on Responses API specification
        if eventType == "status_update" {
            if let statusData = await parseStatusUpdate(data) {
                statusMessage = statusData.message
                if let status = statusData.status {
                    isSearching = (status == "web_search_searching" || status == "web_search_started")
                }
            }
        } else if eventType == "text_delta" {
            if let delta = await parseTextDelta(data) {
                accumulatedText += delta
                
                // Since we're already on @MainActor, no need for MainActor.run
                // Measure UI update performance
                HangDetector.shared.measureMainThreadOperation(
                    operation: {
                        // Update both allMessages and displayed messages
                        let messageId = messages[messageIndex].id
                        if let allMessageIndex = allMessages.lastIndex(where: { $0.id == messageId }) {
                            allMessages[allMessageIndex].content = accumulatedText
                        }
                        
                        // Create a new message instance to ensure SwiftUI detects the change
                        var updatedMessage = messages[messageIndex]
                        updatedMessage.content = accumulatedText
                        
                        // Signal change before updating
                        objectWillChange.send()
                        messages[messageIndex] = updatedMessage
                        
                        statusMessage = nil
                        isSearching = false
                    },
                    description: "UI update for streaming text"
                )
            }
        } else if eventType == "response_complete" {
            if let responseData = await parseResponseComplete(data, accumulatedText: accumulatedText) {
                // Since we're already on @MainActor, no need for MainActor.run
                // Measure UI update performance for completion events
                HangDetector.shared.measureMainThreadOperation(
                    operation: {
                        // Update both allMessages and displayed messages
                        let messageId = messages[messageIndex].id
                        if let allMessageIndex = allMessages.lastIndex(where: { $0.id == messageId }) {
                            allMessages[allMessageIndex].content = responseData.advice.mainAdvice
                            allMessages[allMessageIndex].structuredAdvice = responseData.advice
                        }
                        
                        var updatedMessage = messages[messageIndex]
                        updatedMessage.content = responseData.advice.mainAdvice
                        updatedMessage.structuredAdvice = responseData.advice
                        
                        // Signal change before updating
                        objectWillChange.send()
                        messages[messageIndex] = updatedMessage
                        
                        statusMessage = nil
                        isSearching = false
                    },
                    description: "UI update for response completion"
                )
                
                // Return the response ID for conversation tracking
                return responseData.responseId
            }
        } else if eventType == "error" {
            if let errorMessage = await parseError(data) {
                // Update both allMessages and displayed messages
                let messageId = messages[messageIndex].id
                if let allMessageIndex = allMessages.lastIndex(where: { $0.id == messageId }) {
                    allMessages[allMessageIndex].content = "Error: \(errorMessage)"
                }
                
                var updatedMessage = messages[messageIndex]
                updatedMessage.content = "Error: \(errorMessage)"
                messages[messageIndex] = updatedMessage
                currentErrorMessage = "Error: \(errorMessage)"
            }
        } else if eventType == "response_created" {
            // Handle response creation event to potentially extract response ID early
            if let responseId = await parseResponseCreated(data) {
                return responseId
            }
        } else if eventType == "response.web_search_call.searching" || eventType == "web_search_started" {
            // Handle web search events
            statusMessage = "🔍 Searching the web..."
            isSearching = true
        } else if eventType == "response.web_search_call.completed" || eventType == "web_search_completed" {
            // Handle web search completion
            statusMessage = "✅ Web search completed"
            isSearching = false
        } else if eventType == "response.in_progress" {
            // Handle response in progress
            statusMessage = "💭 Assistant is thinking..."
            isSearching = false
        } else if eventType == "response.text.delta" {
            // Handle official Responses API text delta format
            if let delta = await parseTextDelta(data) {
                accumulatedText += delta
                
                // Since we're already on @MainActor, no need for MainActor.run
                // Measure UI update performance for official delta events
                HangDetector.shared.measureMainThreadOperation(
                    operation: {
                        // Update both allMessages and displayed messages
                        let messageId = messages[messageIndex].id
                        if let allMessageIndex = allMessages.lastIndex(where: { $0.id == messageId }) {
                            allMessages[allMessageIndex].content = accumulatedText
                        }
                        
                        var updatedMessage = messages[messageIndex]
                        updatedMessage.content = accumulatedText
                        
                        objectWillChange.send()
                        messages[messageIndex] = updatedMessage
                        
                        statusMessage = nil
                        isSearching = false
                    },
                    description: "UI update for official text delta"
                )
            }
        } else if eventType == "response.completed" {
            // Handle official completion event
            statusMessage = nil
            isSearching = false
        }
        // Note: Unhandled event types are silently ignored per Responses API best practices
        return nil
    }
    
    func saveConversation() {
        updateCurrentConversation()
    }
    
    // Start a new conversation by resetting context
    func startNewConversation() {
        guard let manager = conversationManager else { return }
        
        // Create new conversation
        let newConversation = manager.createNewConversation()
        currentConversationId = newConversation.id
        
        // Reset conversation state with message windowing
        let welcomeMessage = Message(role: .assistant, content: "Welcome to Fantasy Genius! How can I help you today?")
        allMessages = [welcomeMessage]
        messages = displayMessages
        
        // Clear error states
        currentErrorMessage = nil
        isLoading = false
        isSearching = false
        streamingText = ""
        statusMessage = nil
    }
    
    // Reset current conversation context (useful for testing or troubleshooting)
    func resetConversationContext() {
        guard let manager = conversationManager,
              let conversationId = currentConversationId,
              var conversation = manager.conversations.first(where: { $0.id == conversationId }) else {
            return
        }
        
        // Reset the response ID to start fresh context
        conversation.resetConversationState()
        manager.updateConversation(conversation)
        
        // Clear error states
        currentErrorMessage = nil
    }
    
    // MARK: - Public Interface Methods
    
    /// Clear current error message
    func clearError() {
        currentErrorMessage = nil
    }
    
    /// Add a message to the conversation
    func addMessage(_ message: Message) {
        allMessages.append(message)
        messages = displayMessages
        updateCurrentConversation()
    }
    
    /// Clear draft attachments
    func clearDraftAttachments() {
        draftAttachmentData.removeAll()
    }
    
    /// Set loading state
    private func setLoadingState(_ loading: Bool) {
        isLoading = loading
        if !loading {
            isSearching = false
            statusMessage = nil
        }
    }
    
    /// Set error state with message
    private func setError(_ message: String) {
        currentErrorMessage = message
        setLoadingState(false)
    }
}
