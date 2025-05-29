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
        
        // Add a placeholder for the assistant's response
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
        
        init(messageIndex: Int, viewModel: ChatViewModel?, completion: @escaping @Sendable () -> Void) {
            self.messageIndex = messageIndex
            self.viewModel = viewModel
            self.completion = completion
        }
        
        nonisolated func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
            guard let string = String(data: data, encoding: .utf8) else { return }
            
            Task { @MainActor in
                buffer += string
                
                // Process complete SSE events (terminated by double newlines)
                let events = buffer.components(separatedBy: "\n\n")
                buffer = events.last ?? "" // Keep incomplete event in buffer
                
                for event in events.dropLast() {
                    await processSSEEvent(event)
                }
            }
        }
        
        nonisolated func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
            Task { @MainActor in
                if let error = error {
                    print("SSE stream completed with error: \(error)")
                } else {
                    print("SSE stream completed successfully")
                }
                completion()
            }
        }
        
        private func processSSEEvent(_ event: String) async {
            let lines = event.components(separatedBy: "\n")
            var data: String?
            
            for line in lines {
                if line.hasPrefix("data: ") {
                    data = String(line.dropFirst(6))
                    break // Only need the data line
                }
            }
            
            guard let data = data else { return }
            
            do {
                if let jsonData = data.data(using: .utf8),
                   let eventData = try JSONSerialization.jsonObject(with: jsonData) as? [String: Any] {
                    
                    await handleSSEData(eventData)
                }
            } catch {
                print("Failed to parse SSE data: \(error)")
            }
        }
        
        private func handleSSEData(_ eventData: [String: Any]) async {
            guard let viewModel = viewModel else { return }
            
            if let status = eventData["status"] as? String, status == "searching" {
                viewModel.isSearching = true
                viewModel.streamingText = "🔍 Searching the web for current information..."
            }
            else if let delta = eventData["delta"] as? String {
                viewModel.isSearching = false
                accumulatedText += delta
                viewModel.streamingText = accumulatedText
                
                if messageIndex < viewModel.messages.count {
                    viewModel.messages[messageIndex].content = accumulatedText
                }
            }
            else if let status = eventData["status"] as? String,
                    status == "complete",
                    let finalJsonData = eventData["final_json"] as? [String: Any] {
                
                do {
                    let structuredData = try JSONSerialization.data(withJSONObject: finalJsonData)
                    let parsedAdvice = try JSONDecoder().decode(StructuredAdviceResponse.self, from: structuredData)
                    
                    viewModel.isSearching = false
                    viewModel.streamingText = ""
                    
                    if messageIndex < viewModel.messages.count {
                        viewModel.messages[messageIndex].content = parsedAdvice.mainAdvice
                        viewModel.messages[messageIndex].structuredAdvice = parsedAdvice
                    }
                } catch {
                    print("Failed to parse final structured advice: \(error)")
                    viewModel.isSearching = false
                    viewModel.streamingText = ""
                }
            }
            else if let error = eventData["error"] as? String,
                    let message = eventData["message"] as? String {
                
                viewModel.isSearching = false
                viewModel.streamingText = ""
                
                if messageIndex < viewModel.messages.count {
                    viewModel.messages[messageIndex].content = "Error: \(error) - \(message)"
                }
                viewModel.currentErrorMessage = "Error: \(error) - \(message)"
            }
        }
    }
    
    func saveConversation() {
        updateCurrentConversation()
    }
}
