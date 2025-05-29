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
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 0) { // Ensure VStack aligns content to leading
            sidebarHeader
            Divider()
            recentChatsList
            Spacer() // Pushes newChatButton to the bottom
            newChatButton
        }
        .background(Color(.systemGroupedBackground))
        // The overlay for shadow is only needed for compact mode,
        // NavigationSplitView handles its own separators.
        .overlay(alignment: .trailing) {
            if horizontalSizeClass == .compact {
                Rectangle()
                    .fill(Color.black.opacity(0.12))
                    .frame(width: 1)
                    .edgesIgnoringSafeArea(.vertical) // Extend shadow to full height
            }
        }
        // For NavigationSplitView, it's better to set a min/ideal/max width on the view itself
        // rather than a fixed frame, as done in ContentView.
    }
    
    private var sidebarHeader: some View {
        HStack(spacing: 12) {
            Button(action: {
                showingSettings = true
                // On compact devices, tapping profile might close the sidebar to show settings
                if horizontalSizeClass == .compact && showingSidebar { // Check showingSidebar to avoid unnecessary animation
                    withAnimation(.easeInOut) {
                        showingSidebar = false
                    }
                }
            }) {
                Circle()
                    .fill(Color.blue.gradient)
                    .overlay(Text("FG").font(.subheadline).fontWeight(.semibold).foregroundColor(.white))
                    .frame(width: 40, height: 40)
                    .clipShape(Circle())
            }
            .buttonStyle(PlainButtonStyle())
            .frame(minWidth: 44, minHeight: 44)
            
            VStack(alignment: .leading, spacing: 2) {
                Text("Fantasy Genius").font(.headline).fontWeight(.semibold)
                Text("Recent Chats").font(.caption).foregroundColor(.secondary)
            }
            .padding(.trailing, 8) // Add some padding to prevent text from sticking to the button if it appears
            
            Spacer() // Pushes content to the left and button to the right
            
            // Close sidebar button - only show on compact width where sidebar can be manually closed
            // And only if the `showingSidebar` binding is true (meaning it's the slide-out one)
            if horizontalSizeClass == .compact && showingSidebar {
                Button(action: {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        showingSidebar = false
                    }
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.system(size: 22, weight: .light)) // Lighter, larger close button
                        .foregroundColor(.gray.opacity(0.6))
                }
                .buttonStyle(PlainButtonStyle())
                .frame(minWidth: 44, minHeight: 44)
            }
        }
        .padding(.horizontal, 12) // Adjusted padding
        .padding(.vertical, 10)   // Adjusted padding
        .background(Color(.secondarySystemGroupedBackground).edgesIgnoringSafeArea(.top)) // Extend background to top edge
    }
    
    private var recentChatsList: some View {
        ScrollView {
            LazyVStack(spacing: 0) { // Use LazyVStack for performance and set spacing to 0 for custom dividers
                ForEach(conversationManager.conversations) { conversation in
                    ChatRowView(
                        conversation: conversation,
                        isSelected: selectedConversation?.id == conversation.id,
                        onTap: {
                            selectedConversation = conversation // Update selection
                            // In compact mode, also hide the sidebar
                            if horizontalSizeClass == .compact {
                                withAnimation(.easeInOut(duration: 0.2)) {
                                    showingSidebar = false
                                }
                            }
                        },
                        onDelete: {
                            conversationManager.deleteConversation(conversation)
                            if selectedConversation?.id == conversation.id {
                                selectedConversation = conversationManager.currentConversation
                            }
                        }
                    )
                    
                    // Custom divider, only if not the last item
                    if conversation.id != conversationManager.conversations.last?.id {
                        Divider().padding(.leading, horizontalSizeClass == .regular ? 20 : 16) // Indent divider
                    }
                }
            }
        }
        .scrollIndicators(horizontalSizeClass == .compact ? .hidden : .automatic) // Hide scroll indicators for compact
    }
    
    private var newChatButton: some View {
        Button(action: {
            let newConversation = conversationManager.createNewConversation()
            selectedConversation = newConversation // Switch to the new conversation
            
            // In compact mode, also hide the sidebar
            if horizontalSizeClass == .compact {
                withAnimation(.easeInOut(duration: 0.2)) {
                    showingSidebar = false
                }
            }
        }) {
            HStack(spacing: 12) { // Add spacing to HStack
                Image(systemName: "plus.circle.fill")
                    .font(.system(size: 20, weight: .medium)) // Slightly larger icon
                Text("New Chat")
                    .font(.headline).fontWeight(.semibold) // Bolder text
                Spacer()
            }
            .foregroundColor(.white)
            .padding(.leading, horizontalSizeClass == .regular ? 16 : 12) // Indent content slightly
            .padding(.trailing, 12)
            .padding(.vertical, 14) // More vertical padding
            .frame(minHeight: 50)    // Increased height
            .background(Color.accentColor)
            .clipShape(RoundedRectangle(cornerRadius: 10))
        }
        .buttonStyle(PlainButtonStyle())
        .padding(.horizontal, horizontalSizeClass == .regular ? 16 : 12) // Outer padding for the button
        .padding(.bottom, UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .first?.windows.first?.safeAreaInsets.bottom ?? 16)
    }
}

struct ChatRowView: View {
    let conversation: Conversation
    let isSelected: Bool
    let onTap: () -> Void
    let onDelete: () -> Void
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    
    @State private var showingDeleteAlert = false
    
    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(conversation.title)
                    .font(.system(size: 16, weight: .medium)) // Slightly adjusted font
                    .lineLimit(1)
                
                Text(conversation.preview)
                    .font(.system(size: 14)) // Slightly adjusted font
                    .foregroundColor(.secondary)
                    .lineLimit(horizontalSizeClass == .regular ? 2 : 1) // More preview lines on iPad
                
                Text(relativeDateString(from: conversation.lastMessageDate))
                    .font(.caption2)
                    .foregroundColor(.gray) // Consistent gray for less important text
            }
            
            Spacer()
            
            Button(action: {
                showingDeleteAlert = true
            }) {
                Image(systemName: "trash.fill") // Filled trash icon
                    .font(.system(size: 16, weight: .medium)) // Adjusted size
                    .foregroundColor(.red.opacity(0.9)) // Slightly stronger red
            }
            .buttonStyle(PlainButtonStyle())
            .frame(minWidth: 44, minHeight: 44)
            .opacity(isSelected ? 1.0 : 0.6) // Adjust opacity
        }
        .padding(.horizontal, horizontalSizeClass == .regular ? 16 : 12) // Consistent padding
        .padding(.vertical, 12) // Consistent padding
        .background(isSelected ? Color.accentColor.opacity(0.25) : Color.clear) // Slightly more pronounced selection
        .cornerRadius(8) // Always apply corner radius for visual consistency, tap target
        .contentShape(Rectangle()) // Ensure entire area is tappable
        .onTapGesture { onTap() } // onTap for the whole row
        .alert("Delete Chat", isPresented: $showingDeleteAlert) {
            Button("Cancel", role: .cancel) {}
            Button("Delete", role: .destructive) { onDelete() }
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