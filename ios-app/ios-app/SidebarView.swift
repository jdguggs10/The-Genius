//
//  SidebarView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI

struct SidebarView: View {
    @ObservedObject var conversationManager: ConversationManager
    @Binding var selectedConversation: Conversation?
    @Binding var showingSidebar: Bool
    @Binding var showingSettings: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            // Header with profile picture
            sidebarHeader
            
            Divider()
            
            // Recent chats list
            recentChatsList
            
            Spacer()
            
            // New chat button
            newChatButton
        }
        .frame(width: 280)
        .background(Color(.systemGroupedBackground))
        .overlay(alignment: .trailing) {
            // Subtle shadow for depth
            Rectangle()
                .fill(Color.black.opacity(0.1))
                .frame(width: 1)
        }
    }
    
    private var sidebarHeader: some View {
        HStack(spacing: 12) {
            // Profile picture button
            Button(action: {
                showingSettings = true
                showingSidebar = false
            }) {
                AsyncImage(url: URL(string: "https://via.placeholder.com/40x40/007AFF/FFFFFF?text=FG")) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } placeholder: {
                    Circle()
                        .fill(.blue.gradient)
                        .overlay {
                            Text("FG")
                                .font(.subheadline)
                                .fontWeight(.semibold)
                                .foregroundColor(.white)
                        }
                }
                .frame(width: 40, height: 40)
                .clipShape(Circle())
            }
            .buttonStyle(PlainButtonStyle())
            
            VStack(alignment: .leading, spacing: 2) {
                Text("Fantasy Genius")
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Text("Recent Chats")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // Close sidebar button
            Button(action: {
                withAnimation(.easeInOut(duration: 0.3)) {
                    showingSidebar = false
                }
            }) {
                Image(systemName: "xmark")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.secondary)
                    .frame(width: 24, height: 24)
                    .background(Color(.systemGray5))
                    .clipShape(Circle())
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color(.secondarySystemGroupedBackground))
    }
    
    private var recentChatsList: some View {
        ScrollView {
            LazyVStack(spacing: 0) {
                ForEach(conversationManager.conversations) { conversation in
                    ChatRowView(
                        conversation: conversation,
                        isSelected: selectedConversation?.id == conversation.id,
                        onTap: {
                            conversationManager.switchToConversation(conversation)
                            selectedConversation = conversation
                            
                            withAnimation(.easeInOut(duration: 0.3)) {
                                showingSidebar = false
                            }
                        },
                        onDelete: {
                            conversationManager.deleteConversation(conversation)
                            // Update selected conversation if needed
                            if selectedConversation?.id == conversation.id {
                                selectedConversation = conversationManager.currentConversation
                            }
                        }
                    )
                    
                    if conversation.id != conversationManager.conversations.last?.id {
                        Divider()
                            .padding(.leading, 16)
                    }
                }
            }
        }
        .scrollIndicators(.hidden)
    }
    
    private var newChatButton: some View {
        Button(action: {
            let newConversation = conversationManager.createNewConversation()
            selectedConversation = newConversation
            
            withAnimation(.easeInOut(duration: 0.3)) {
                showingSidebar = false
            }
        }) {
            HStack {
                Image(systemName: "plus")
                    .font(.system(size: 16, weight: .medium))
                
                Text("New Chat")
                    .font(.headline)
                    .fontWeight(.medium)
                
                Spacer()
            }
            .foregroundColor(.white)
            .padding(.horizontal, 20)
            .padding(.vertical, 14)
            .background(Color.blue)
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, 16)
        .padding(.bottom, 20)
    }
}

struct ChatRowView: View {
    let conversation: Conversation
    let isSelected: Bool
    let onTap: () -> Void
    let onDelete: () -> Void
    
    @State private var showingDeleteAlert = false
    
    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(conversation.title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .lineLimit(1)
                
                Text(conversation.preview)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
                
                Text(relativeDateString(from: conversation.lastMessageDate))
                    .font(.caption2)
                    .foregroundColor(.secondary.opacity(0.6))
            }
            
            Spacer()
            
            // Delete button
            Button(action: {
                showingDeleteAlert = true
            }) {
                Image(systemName: "trash")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(.red)
                    .frame(width: 24, height: 24)
                    .background(Color(.systemGray6))
                    .clipShape(Circle())
            }
            .buttonStyle(PlainButtonStyle())
            .opacity(0.7)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(isSelected ? Color(.systemGray5) : Color.clear)
        .contentShape(Rectangle())
        .onTapGesture {
            onTap()
        }
        .alert("Delete Chat", isPresented: $showingDeleteAlert) {
            Button("Cancel", role: .cancel) { }
            Button("Delete", role: .destructive) {
                onDelete()
            }
        } message: {
            Text("Are you sure you want to delete this chat? This action cannot be undone.")
        }
    }
    
    private func relativeDateString(from date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.dateTimeStyle = .named
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

#Preview {
    SidebarView(
        conversationManager: ConversationManager(),
        selectedConversation: .constant(nil),
        showingSidebar: .constant(true),
        showingSettings: .constant(false)
    )
} 