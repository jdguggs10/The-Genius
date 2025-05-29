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
    
    func setConversationManager(_ manager: ConversationManager) {
        self.conversationManager = manager
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
        request.timeoutInterval = 300 // 5 minutes
        
        // Use simple, standard URLSession configuration
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        
        // Prepare the conversation payload
        let conversationPayloads = self.messages.filter { $0.id != assistantMessagePlaceholder.id }.map {
            MessagePayload(role: $0.role, content: $0.content)
        }
        let adviceRequest = AdviceRequestPayload(conversation: conversationPayloads)

        do {
            request.httpBody = try JSONEncoder().encode(adviceRequest)
            print("Making SSE request to: \(url)")
            
        } catch {
            messages[assistantMessageIndex].content = "Error: Could not encode request: \(error.localizedDescription)"
            currentErrorMessage = "Error: Could not encode request: \(error.localizedDescription)"
            isLoading = false
            return
        }
        
        // Use URLSessionDataTask for proper SSE handling
        await withCheckedContinuation { continuation in
            // Create a custom delegate to handle streaming data
            let delegate = SSEDelegate(messageIndex: assistantMessageIndex, viewModel: self) { [weak self] in
                Task { @MainActor in
                    self?.isLoading = false
                    self?.isSearching = false
                    self?.streamingText = ""
                    self?.statusMessage = nil
                    self?.saveConversation()
                }
                continuation.resume()
            }
            
            // Create session with our delegate
            let delegateSession = URLSession(configuration: config, delegate: delegate, delegateQueue: nil)
            let streamingTask = delegateSession.dataTask(with: request)
            streamingTask.resume()
        }
    }
    
    // MARK: - SSE Delegate
    
    @MainActor
    final class SSEDelegate: NSObject, URLSessionDataDelegate {
        private var buffer = ""
        private var accumulatedText = ""
        private let messageIndex: Int
        private weak var viewModel: ChatViewModel?
        private let completion: @Sendable () -> Void
        private var currentEventType: String? = nil
        
        init(messageIndex: Int, viewModel: ChatViewModel?, completion: @escaping @Sendable () -> Void) {
            self.messageIndex = messageIndex
            self.viewModel = viewModel
            self.completion = completion
        }
        
        nonisolated func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
            guard let string = String(data: data, encoding: .utf8) else { return }
            
            Task { @MainActor in
                buffer += string
                
                while let eventRange = buffer.range(of: "\n\n") {
                    let eventString = String(buffer[..<eventRange.lowerBound])
                    buffer.removeSubrange(...eventRange.upperBound)
                    await processSSEEvent(eventString)
                }
            }
        }
        
        nonisolated func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
            Task { @MainActor in
                if let viewModel = self.viewModel {
                    if let error = error {
                        print("SSE stream completed with error: \(error)")
                        viewModel.messages[messageIndex].content = "Error: \(error.localizedDescription)"
                        viewModel.currentErrorMessage = "Error: \(error.localizedDescription)"
                    } else {
                        print("SSE stream completed successfully")
                        if !accumulatedText.isEmpty && (viewModel.messages[messageIndex].structuredAdvice == nil && viewModel.messages[messageIndex].content.isEmpty) {
                            viewModel.messages[messageIndex].content = accumulatedText
                        }
                    }
                    viewModel.statusMessage = nil
                    viewModel.streamingText = ""
                }
                completion()
            }
        }
        
        private func processSSEEvent(_ eventString: String) async {
            let lines = eventString.components(separatedBy: "\n")
            var eventType: String? = nil
            var dataString: String? = nil
            
            for line in lines {
                if line.hasPrefix("event: ") {
                    eventType = String(line.dropFirst(7)).trimmingCharacters(in: .whitespacesAndNewlines)
                } else if line.hasPrefix("data: ") {
                    dataString = String(line.dropFirst(6))
                }
            }
            
            if let type = eventType {
                self.currentEventType = type
            }

            if let jsonDataString = dataString {
                do {
                    if let jsonData = jsonDataString.data(using: .utf8),
                       let parsedJson = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any] {
                        await handleSSEData(eventType: self.currentEventType, data: parsedJson)
                    } else if jsonDataString.lowercased() == "[done]" && self.currentEventType?.lowercased() == "response_complete" {
                         await handleSSEData(eventType: self.currentEventType, data: ["status": "complete", "final_json": ["main_advice": accumulatedText]])
                    }
                } catch {
                    print("Failed to parse SSE data string '\(jsonDataString)': \(error)")
                }
            } else if self.currentEventType != nil && dataString == nil {
                 print("Received event type '\(self.currentEventType ?? "unknown")' without data.")
            }
            
            if dataString != nil {
                self.currentEventType = nil
            }
        }
        
        private func handleSSEData(eventType: String?, data: [String: Any]) async {
            guard let viewModel = viewModel else { return }

            let typeToProcess = eventType

            if typeToProcess == "status_update" {
                if let message = data["message"] as? String {
                    viewModel.statusMessage = message
                    viewModel.streamingText = ""
                    if viewModel.messages.indices.contains(messageIndex) {
                        viewModel.messages[messageIndex].content = message
                    }
                }
                if let statusDetail = data["status"] as? String {
                    viewModel.isSearching = (statusDetail == "web_search_searching" || statusDetail == "web_search_started")
                }
            } else if typeToProcess == "text_delta" {
                viewModel.statusMessage = nil
                viewModel.isSearching = false
                if let delta = data["delta"] as? String {
                    accumulatedText += delta
                    if viewModel.messages.indices.contains(messageIndex) {
                        viewModel.messages[messageIndex].content = accumulatedText
                    }
                }
            } else if typeToProcess == "response_complete" {
                viewModel.statusMessage = nil
                viewModel.isSearching = false
                viewModel.streamingText = ""
                if let finalJson = data["final_json"] as? [String: Any] {
                    let mainAdvice = finalJson["main_advice"] as? String ?? accumulatedText
                    let reasoning = finalJson["reasoning"] as? String
                    let confidence = finalJson["confidence_score"] as? Double
                    let modelId = finalJson["model_identifier"] as? String
                    
                    let structuredAdvice = StructuredAdviceResponse(
                        main_advice: mainAdvice,
                        reasoning: reasoning,
                        confidence_score: confidence,
                        alternatives: [],
                        model_identifier: modelId
                    )
                    if viewModel.messages.indices.contains(messageIndex) {
                        viewModel.messages[messageIndex].content = mainAdvice
                        viewModel.messages[messageIndex].structuredAdvice = structuredAdvice
                    }
                } else if !accumulatedText.isEmpty {
                    if viewModel.messages.indices.contains(messageIndex) {
                        viewModel.messages[messageIndex].content = accumulatedText
                    }
                }
                accumulatedText = ""
            } else if typeToProcess == "error" {
                viewModel.statusMessage = nil
                viewModel.isSearching = false
                if let errorMessage = data["message"] as? String {
                    if viewModel.messages.indices.contains(messageIndex) {
                        viewModel.messages[messageIndex].content = "Error: \(errorMessage)"
                    }
                    viewModel.currentErrorMessage = "Error: \(errorMessage)"
                }
            } else {
                if let status = data["status"] as? String, status == "searching" {
                    viewModel.statusMessage = "🔍 Searching the web..."
                    if viewModel.messages.indices.contains(messageIndex) {
                        viewModel.messages[messageIndex].content = "🔍 Searching the web..."
                    }
                    viewModel.isSearching = true
                } else if let delta = data["delta"] as? String {
                    viewModel.statusMessage = nil
                    viewModel.isSearching = false
                    accumulatedText += delta
                    if viewModel.messages.indices.contains(messageIndex) {
                        viewModel.messages[messageIndex].content = accumulatedText
                    }
                } else if let finalJson = data["final_json"] as? [String: Any] {
                    viewModel.statusMessage = nil
                    viewModel.isSearching = false
                    viewModel.streamingText = ""
                    let mainAdvice = finalJson["main_advice"] as? String ?? accumulatedText
                    let structuredAdvice = StructuredAdviceResponse(main_advice: mainAdvice)
                     if viewModel.messages.indices.contains(messageIndex) {
                        viewModel.messages[messageIndex].content = mainAdvice
                        viewModel.messages[messageIndex].structuredAdvice = structuredAdvice
                    }
                    accumulatedText = ""
                } else if let errorMessage = data["error"] as? String {
                    viewModel.statusMessage = nil
                    if viewModel.messages.indices.contains(messageIndex) {
                        viewModel.messages[messageIndex].content = "Error: \(errorMessage)"
                    }
                     viewModel.currentErrorMessage = "Error: \(errorMessage)"
                }
                 logger.debug("Processed data with type: \(typeToProcess ?? "legacy format") - Data: \(data)")
            }
        }
        
        private func saveConversation() {
            guard let viewModel = viewModel else { return }
            viewModel.updateCurrentConversation()
        }
    }
    
    func saveConversation() {
        updateCurrentConversation()
    }
}

struct MessagePayload: Codable {
    let role: MessageRole
    let content: String
}

struct AdviceRequestPayload: Codable {
    let conversation: [MessagePayload]
    // Add enable_web_search if your backend expects it
    // var enable_web_search: Bool = false 
}

struct StructuredAdviceResponse: Codable, Hashable {
    var main_advice: String
    var reasoning: String? = nil
    var confidence_score: Double? = nil
    var alternatives: [AlternativeAdvice]? = []
    var model_identifier: String? = nil
}

struct AlternativeAdvice: Codable, Hashable {
    var player: String
    var reason: String? = nil
}
