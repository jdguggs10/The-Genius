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
    
    // Use your backend URL - change this to match your deployment
    private let backendURLString = "https://genius-backend-nhl3.onrender.com/advice" // Updated to Render URL
    
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
        
        Task {
            await fetchStreamingStructuredAdvice()
        }
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
        
        var accumulatedText = ""
        var eventBuffer = ""
        
        do {
            let (stream, response) = try await URLSession.shared.bytes(for: request)
            
            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode != 200 {
                var errorBodyString = "No additional error information from server."
                var tempErrorData = Data()
                for try await byteChunk in stream {
                    tempErrorData.append(byteChunk)
                }
                if !tempErrorData.isEmpty {
                    errorBodyString = String(data: tempErrorData, encoding: .utf8) ?? "Could not decode error body."
                }
                messages[assistantMessageIndex].content = "Error: Server returned status \(httpResponse.statusCode). \(errorBodyString)"
                currentErrorMessage = "Error: Server returned status \(httpResponse.statusCode). \(errorBodyString)"
                isLoading = false
                saveConversation()
                return
            }
            
            // Process Server-Sent Events stream
            for try await byteChunk in stream {
                let chunkString = String(data: Data([byteChunk]), encoding: .utf8) ?? ""
                eventBuffer += chunkString
                
                // Process complete lines
                let lines = eventBuffer.components(separatedBy: .newlines)
                eventBuffer = lines.last ?? "" // Keep incomplete line in buffer
                
                for line in lines.dropLast() {
                    await processSSELine(line, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
                }
            }
            
            // Process any remaining buffer
            if !eventBuffer.isEmpty {
                await processSSELine(eventBuffer, messageIndex: assistantMessageIndex, accumulatedText: &accumulatedText)
            }
            
            currentErrorMessage = nil
            
        } catch let decodingError as DecodingError {
            let errorDetails = "Decoding Error: \(decodingError.localizedDescription). Details: \(decodingError)"
            messages[assistantMessageIndex].content = errorDetails
            currentErrorMessage = errorDetails
            print("Decoding Error: \(decodingError)")
        } catch {
            messages[assistantMessageIndex].content = "Error processing stream: \(error.localizedDescription)"
            currentErrorMessage = "Error processing stream: \(error.localizedDescription)"
            print("Streaming/Processing Error: \(error)")
        }
        
        isLoading = false
        isSearching = false
        streamingText = ""
        saveConversation()
    }
    
    private func processSSELine(_ line: String, messageIndex: Int, accumulatedText: inout String) async {
        if line.hasPrefix("event: ") {
            // Event type line - we can track this for different handling if needed
            return
        }
        
        if line.hasPrefix("data: ") {
            let dataString = String(line.dropFirst(6)) // Remove "data: "
            
            do {
                if let data = dataString.data(using: .utf8) {
                    let eventData = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                    
                    if let status = eventData?["status"] as? String, status == "searching" {
                        // Handle web search status
                        await MainActor.run {
                            isSearching = true
                            streamingText = "🔍 Searching the web for current information..."
                        }
                    }
                    else if let delta = eventData?["delta"] as? String {
                        // Handle text delta - update message progressively
                        isSearching = false
                        accumulatedText += delta
                        
                        // Update UI on main thread
                        await MainActor.run {
                            streamingText = accumulatedText
                            if messageIndex < messages.count {
                                messages[messageIndex].content = accumulatedText
                            }
                        }
                    }
                    else if let status = eventData?["status"] as? String,
                            status == "complete",
                            let finalJsonData = eventData?["final_json"] as? [String: Any] {
                        
                        // Handle final structured advice
                        do {
                            let structuredData = try JSONSerialization.data(withJSONObject: finalJsonData)
                            let parsedAdvice = try JSONDecoder().decode(StructuredAdviceResponse.self, from: structuredData)
                            
                            await MainActor.run {
                                isSearching = false
                                streamingText = ""
                                if messageIndex < messages.count {
                                    messages[messageIndex].content = parsedAdvice.mainAdvice
                                    messages[messageIndex].structuredAdvice = parsedAdvice
                                }
                            }
                        } catch {
                            print("Failed to parse final structured advice: \(error)")
                            // Keep the accumulated text as fallback
                            await MainActor.run {
                                isSearching = false
                                streamingText = ""
                            }
                        }
                    }
                    else if let error = eventData?["error"] as? String,
                            let message = eventData?["message"] as? String {
                        
                        // Handle error events
                        await MainActor.run {
                            isSearching = false
                            streamingText = ""
                            if messageIndex < messages.count {
                                messages[messageIndex].content = "Error: \(error) - \(message)"
                            }
                            currentErrorMessage = "Error: \(error) - \(message)"
                        }
                    }
                }
            } catch {
                print("Failed to parse SSE data: \(error)")
            }
        }
    }
    
    func saveConversation() {
        if let encoded = try? JSONEncoder().encode(messages) {
            UserDefaults.standard.set(encoded, forKey: "current_conversation")
        }
    }
    
    func loadConversation() {
        if let data = UserDefaults.standard.data(forKey: "current_conversation"),
           let decoded = try? JSONDecoder().decode([Message].self, from: data) {
            messages = decoded
            currentErrorMessage = nil // Clear error messages on load
        } else {
            messages = [
                Message(role: .assistant, content: "Welcome to Fantasy Genius! How can I help you today?")
            ]
        }
    }
}
