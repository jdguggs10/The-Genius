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
    @Published private(set) var messages: [ChatMessage] = []
    @Published private(set) var isLoading: Bool = false
    @Published private(set) var isSearching: Bool = false
    @Published private(set) var streamingText: String = ""
    @Published private(set) var streamingMessageId: String? = nil
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
    private var allMessages: [ChatMessage] = [] // Complete conversation history
    
    /// Computed property that returns windowed messages for display
    var displayMessages: [ChatMessage] {
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
            // Use streamingSession instead of URLSession.shared for extended timeouts
            let (data, _) = try await streamingSession.data(from: url)
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
            let welcomeMessage = ChatMessage(id: UUID().uuidString, createdAt: Date(), role: .assistant, content: "Welcome to Fantasy Genius! How can I help you today?", attachments: [], structuredAdvice: nil)
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
            ChatMessage.Attachment(type: .image, data: data) // Assuming images for now
        }
        
        let userMessage = ChatMessage(
            id: UUID().uuidString,
            createdAt: Date(),
            role: .user,
            content: trimmedInput,
            attachments: attachments,
            structuredAdvice: nil
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
        await performStreamingRequest()
    }
    
    // Track active streaming task to allow cancellation
    private var activeStreamingTask: Task<Void, Never>? = nil
    
    private func performStreamingRequest() async {
        // Cancel any existing streaming task before starting a new one
        activeStreamingTask?.cancel()
        
        // Create a new task for this streaming request
        activeStreamingTask = Task { [weak self] in
            guard let self = self else { return }
            
            self.setLoadingState(true)
            self.streamingText = ""
            self.statusMessage = nil
            self.currentErrorMessage = nil
            
            let assistantMessagePlaceholder = ChatMessage(
                id: UUID().uuidString,
                createdAt: Date(),
                role: .assistant,
                content: "",
                attachments: [],
                structuredAdvice: nil
            )

            // Add to both allMessages and displayed messages with windowing
            self.allMessages.append(assistantMessagePlaceholder)
            self.messages = self.displayMessages
            self.streamingMessageId = assistantMessagePlaceholder.id
            
            // Find the placeholder in the displayed messages (not allMessages)
            guard let assistantMessageIndex = self.messages.lastIndex(where: { $0.id == assistantMessagePlaceholder.id }) else {
                self.setError("Internal error: Could not find placeholder message.")
                return
            }

            guard let url = URL(string: self.backendURLString) else {
                // Update both the displayed message and allMessages
                if let allMessageIndex = self.allMessages.lastIndex(where: { $0.id == assistantMessagePlaceholder.id }) {
                    self.allMessages[allMessageIndex].content = "Error: Invalid backend URL configured."
                }
                self.messages[assistantMessageIndex].content = "Error: Invalid backend URL configured."
                self.setError("Error: Invalid backend URL configured.")
                return
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.setValue("text/event-stream", forHTTPHeaderField: "Accept")
            request.setValue("no-cache", forHTTPHeaderField: "Cache-Control")
            request.setValue("keep-alive", forHTTPHeaderField: "Connection")
            
            // Get the current conversation to check for last response ID
            guard let manager = self.conversationManager,
                  let conversationId = self.currentConversationId,
                  var conversation = manager.conversations.first(where: { $0.id == conversationId }) else {
                
                self.isLoading = false
                return
            }
            
            // Get the latest user message (excluding the placeholder assistant message)
            guard let latestUserMessage = self.messages.dropLast().last(where: { $0.role == .user }) else {
                self.currentErrorMessage = "Error: No user message found."
                self.isLoading = false
                return
            }
            
            // Get the model to use
            let modelToUse = await self.getModelToUse()
            
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
                self.messages[assistantMessageIndex].content = "Error: Could not encode request: \(error.localizedDescription)"
                self.setError("Error: Could not encode request: \(error.localizedDescription)")
                return
            }
            
            // Use the streaming session with proper configuration
            do {
                let streamTask = self.streamingSession.dataTask(with: request) { data, response, error in
                    // This is a fallback for handling immediate task failures
                    if let error = error {
                        Task { @MainActor in
                            self.messages[assistantMessageIndex].content = "Network error: \(error.localizedDescription)"
                            self.setError("Network error: \(error.localizedDescription)")
                            self.setLoadingState(false)
                        }
                    }
                }
                
                // Set up cancellation handler
                Task {
                    await Task.yield() // Allow the task to start
                    try? await Task.sleep(nanoseconds: 100_000_000) // Small delay to ensure task starts
                    
                    // Check if this task was cancelled and cancel the stream if needed
                    for _ in 0..<600 { // Loop for up to 10 minutes (600 seconds)
                        if Task.isCancelled || self.activeStreamingTask?.isCancelled == true {
                            streamTask.cancel()
                            break
                        }
                        try? await Task.sleep(nanoseconds: 1_000_000_000) // Check every second
                    }
                }
                
                // Start the task but process the data manually with async/await
                streamTask.resume()
                
                // Set up a manual implementation of the bytes streaming
                let (asyncBytes, response) = try await self.streamingSession.bytes(for: request)
                
                // Check if task is cancelled before proceeding
                if Task.isCancelled { 
                    streamTask.cancel()
                    return
                }
                
                // Check HTTP response
                if let httpResponse = response as? HTTPURLResponse {
                    if httpResponse.statusCode != 200 {
                        let errorMsg = "HTTP Error: \(httpResponse.statusCode)"
                        self.messages[assistantMessageIndex].content = errorMsg
                        self.setError(errorMsg)
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
                    // Check for task cancellation during streaming
                    if Task.isCancelled {
                        break
                    }
                    
                    lineCount += 1
                    
                    if line.hasPrefix("event: ") {
                        // Process previous event if we have both type and data
                        if let eventType = currentEventType, let data = currentData {
                            eventCount += 1
                            let extractedResponseId = await self.processSSEEvent(eventType: eventType, data: data, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
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
                            let extractedResponseId = await self.processSSEEvent(eventType: eventType, data: data, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
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
                    let extractedResponseId = await self.processSSEEvent(eventType: eventType, data: data, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
                    if let extractedId = extractedResponseId {
                        responseId = extractedId
                    }
                }
                
                // Handle any remaining content
                if !accumulatedText.isEmpty && self.messages[assistantMessageIndex].content.isEmpty {
                    self.messages[assistantMessageIndex].content = accumulatedText
                }
                
                // Update conversation with the new response ID for future context
                if let responseId = responseId {
                    conversation.updateLastResponseId(responseId)
                    manager.updateConversation(conversation)
                }
                
            } catch {
                if Task.isCancelled {
                    print("Streaming task was cancelled")
                } else {
                    let errorMsg = "Network error: \(error.localizedDescription)"
                    self.messages[assistantMessageIndex].content = errorMsg
                    self.setError(errorMsg)
                }
            }
            
            self.setLoadingState(false)
            self.streamingText = ""
            self.streamingMessageId = nil
            self.saveConversation()
            
            // Clean up task reference when complete
            if self.activeStreamingTask?.isCancelled == false {
                self.activeStreamingTask = nil
            }
        }
        
        // Wait for the task to complete
        await activeStreamingTask?.value
    }
    
    // Cancel any active streaming request
    func cancelStreamingRequest() {
        activeStreamingTask?.cancel()
        streamingMessageId = nil
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
            // response_id is returned at the top level of the payload
            let responseId = parsed["response_id"] as? String
            
            // Parse alternatives array
            var alternatives: [Alternative] = []
            if let alternativesArray = finalJson["alternatives"] as? [[String: Any]] {
                alternatives = alternativesArray.compactMap { altDict -> Alternative? in
                    guard let player = altDict["player"] as? String else { return nil }
                    let reason = altDict["reason"] as? String
                    return Alternative(player: player, reason: reason)
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
                streamingText = accumulatedText

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
            }

            if let responseData = await parseResponseComplete(data, accumulatedText: accumulatedText) {
                // Update both allMessages and displayed messages
                let messageId = messages[messageIndex].id
                if let allMessageIndex = allMessages.lastIndex(where: { $0.id == messageId }) {
                    allMessages[allMessageIndex].content = responseData.advice.mainAdvice
                    allMessages[allMessageIndex].structuredAdvice = responseData.advice
                }

                var updatedMessage = messages[messageIndex]
                updatedMessage.content = responseData.advice.mainAdvice
                updatedMessage.structuredAdvice = responseData.advice

                streamingText = responseData.advice.mainAdvice

                // Signal change before updating
                objectWillChange.send()
                messages[messageIndex] = updatedMessage

                statusMessage = nil
                isSearching = false

                // Return the response ID for conversation tracking
                return responseData.responseId
            }

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
                streamingMessageId = nil
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
                streamingText = accumulatedText

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
            }
        } else if eventType == "response.completed" {
            // Handle official completion event
            statusMessage = nil
            isSearching = false
            streamingMessageId = nil
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
        let welcomeMessage = ChatMessage(id: UUID().uuidString, createdAt: Date(), role: .assistant, content: "Welcome to Fantasy Genius! How can I help you today?", attachments: [], structuredAdvice: nil)
        allMessages = [welcomeMessage]
        messages = displayMessages
        
        // Clear error states
        currentErrorMessage = nil
        isLoading = false
        isSearching = false
        streamingText = ""
        streamingMessageId = nil
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
    func addMessage(_ message: ChatMessage) {
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
        streamingMessageId = nil
    }
}
