//
//  Conversation.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import Foundation
import SwiftUI

// Represents a single conversation/chat session
struct Conversation: Identifiable, Codable, Equatable {
    let id: UUID
    var title: String
    var messages: [Message]
    let createdDate: Date
    var lastMessageDate: Date
    var lastResponseId: String? // Track the last OpenAI response ID for context continuity
    
    init(id: UUID = UUID(), title: String = "New Chat", messages: [Message] = []) {
        self.id = id
        self.title = title
        self.messages = messages
        self.createdDate = Date()
        self.lastMessageDate = Date()
        self.lastResponseId = nil
    }
    
    // Custom Equatable implementation
    static func == (lhs: Conversation, rhs: Conversation) -> Bool {
        return lhs.id == rhs.id
    }
    
    // Get the first user message as a preview
    var preview: String {
        if let firstUserMessage = messages.first(where: { $0.role == .user }) {
            return String(firstUserMessage.content.prefix(50)) + (firstUserMessage.content.count > 50 ? "..." : "")
        }
        return "No messages yet"
    }
    
    // Auto-generate title from first message
    mutating func updateTitleFromFirstMessage() {
        if let firstUserMessage = messages.first(where: { $0.role == .user && !$0.content.isEmpty }) {
            // Take first 30 characters for title
            let maxLength = 30
            let content = firstUserMessage.content.trimmingCharacters(in: .whitespacesAndNewlines)
            if content.count > maxLength {
                self.title = String(content.prefix(maxLength)) + "..."
            } else {
                self.title = content
            }
        }
    }
    
    // Update last message date
    mutating func updateLastMessageDate() {
        self.lastMessageDate = Date()
    }
    
    // Update the last response ID after receiving a response from OpenAI
    mutating func updateLastResponseId(_ responseId: String?) {
        self.lastResponseId = responseId
    }
    
    // Reset conversation state (useful for starting fresh)
    mutating func resetConversationState() {
        self.lastResponseId = nil
    }
}

// Manager for handling multiple conversations
@MainActor
class ConversationManager: ObservableObject {
    @Published private(set) var conversations: [Conversation] = []
    @Published var currentConversationId: UUID?
    
    private let conversationsKey = "SavedConversations"
    
    init() {
        // Load conversations asynchronously to avoid blocking app startup
        Task {
            await loadConversationsAsync()
            
            // Create a default conversation if none exist
            if conversations.isEmpty {
                _ = createNewConversation()
            }
        }
    }
    
    var currentConversation: Conversation? {
        get {
            guard let currentId = currentConversationId else { return conversations.first }
            return conversations.first { $0.id == currentId }
        }
        set {
            if let conversation = newValue {
                currentConversationId = conversation.id
                updateConversation(conversation)
            }
        }
    }
    
    func createNewConversation() -> Conversation {
        let newConversation = Conversation()
        appendConversation(newConversation) // Use private method for proper encapsulation
        currentConversationId = newConversation.id
        Task { await saveConversationsAsync() }
        return newConversation
    }
    
    func updateConversation(_ updatedConversation: Conversation) {
        if let index = conversations.firstIndex(where: { $0.id == updatedConversation.id }) {
            conversations[index] = updatedConversation
            Task { await saveConversationsAsync() }
        }
    }
    
    func deleteConversation(withId id: UUID) {
        conversations.removeAll { $0.id == id }
        
        // Update current conversation if needed
        if currentConversationId == id {
            currentConversationId = conversations.first?.id
        }
        
        Task { await saveConversationsAsync() }
    }
    
    func switchToConversation(_ conversation: Conversation) {
        currentConversationId = conversation.id
        
        // Move to front for recency
        if let index = conversations.firstIndex(where: { $0.id == conversation.id }) {
            conversations.move(fromOffsets: IndexSet(integer: index), toOffset: 0)
        }
        
        Task { await saveConversationsAsync() }
    }
    
    private func saveConversations() {
        if let encoded = try? JSONEncoder().encode(conversations) {
            UserDefaults.standard.set(encoded, forKey: conversationsKey)
        }
    }
    
    private func loadConversations() {
        if let data = UserDefaults.standard.data(forKey: conversationsKey),
           let decoded = try? JSONDecoder().decode([Conversation].self, from: data) {
            conversations = decoded
            
            // Set current conversation to the first one if none is selected
            if currentConversationId == nil {
                currentConversationId = conversations.first?.id
            }
        }
    }
    
    private func loadConversationsAsync() async {
        // Perform UserDefaults reading on background queue to avoid blocking startup
        let loadedConversations = await withCheckedContinuation { continuation in
            DispatchQueue.global(qos: .userInitiated).async {
                var result: [Conversation] = []
                if let data = UserDefaults.standard.data(forKey: self.conversationsKey),
                   let decoded = try? JSONDecoder().decode([Conversation].self, from: data) {
                    result = decoded
                }
                continuation.resume(returning: result)
            }
        }
        
        // Update UI state - no need for MainActor.run since class is already @MainActor
        self.conversations = loadedConversations
        
        // Set current conversation to the first one if none is selected
        if self.currentConversationId == nil {
            self.currentConversationId = loadedConversations.first?.id
        }
    }
    
    private func saveConversationsAsync() async {
        let conversationsToSave = self.conversations 
        await Task.detached(priority: .background) {
            do {
                let encoded = try JSONEncoder().encode(conversationsToSave)
                UserDefaults.standard.set(encoded, forKey: self.conversationsKey)
            } catch {
                print("Error encoding conversations: \(error)")
            }
        }.value
    }
    
    // Add method to append new conversation properly
    private func appendConversation(_ conversation: Conversation) {
        conversations.insert(conversation, at: 0) // Add at beginning for recency
    }
} 