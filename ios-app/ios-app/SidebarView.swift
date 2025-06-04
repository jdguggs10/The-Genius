//
//  SidebarView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI

private let appBackgroundColor = Color(red: 253/255, green: 245/255, blue: 230/255) // FDF5E6
private let appPrimaryFontColor = Color(red: 61/255, green: 108/255, blue: 104/255) // 3D6C68

struct SidebarView: View {
    @ObservedObject var conversationManager: ConversationManager
    @Binding var selectedConversation: Conversation?
    @Binding var showingSidebar: Bool
    @Binding var showingSettings: Bool
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @State private var showingNewConversationSheet = false
    @State private var searchText: String = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            
            conversationList
            
            Spacer() // Pushes everything above it up
            
            footer // Settings button
        }
        .background(appBackgroundColor)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .sheet(isPresented: $showingNewConversationSheet) {
            NewConversationSheetView(isPresented: $showingNewConversationSheet) { newTitle in
                var conversation = conversationManager.createNewConversation()
                // Apply the user‑supplied title after creation (avoids the old API mismatch)
                conversation.title = newTitle
                selectedConversation = conversation // Select the new conversation
                if horizontalSizeClass == .compact {
                    showingSidebar = false // Close sidebar in compact mode after creation
                }
            }
        }
    }

    private var header: some View {
        HStack(spacing: 12) {
            Image("appstore")
                .resizable()
                .scaledToFit()
                .frame(width: 28, height: 28)
                .clipShape(RoundedRectangle(cornerRadius: 6))
            
            HStack(spacing: 6) {
                Image(systemName: "magnifyingglass")
                    .font(.system(size: 14))
                    .foregroundColor(appPrimaryFontColor.opacity(0.8))
                
                TextField("Search", text: $searchText)
                    .font(.subheadline)
                    .frame(height: 32)
                
                if !searchText.isEmpty {
                    Button(action: {
                        searchText = ""
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(appPrimaryFontColor.opacity(0.6))
                            .font(.system(size: 14))
                    }
                    .buttonStyle(.plain)
                    .transition(.opacity)
                }
            }
            .padding(.horizontal, 8)
            .frame(height: 32)
            .background(Color(.systemGray6))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(appPrimaryFontColor.opacity(0.2), lineWidth: 1)
            )
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .frame(height: 44)
        .background(appBackgroundColor)
    }

    private var conversationList: some View {
        List(selection: $selectedConversation) {
            ForEach(conversationManager.conversations.filter { searchText.isEmpty || $0.title.localizedCaseInsensitiveContains(searchText) }) { conversation in
                NavigationLink(value: conversation) {
                    Text(conversation.title)
                        .foregroundColor(appPrimaryFontColor) // Font color for conversation titles
                }
                .listRowBackground(selectedConversation == conversation ? appPrimaryFontColor.opacity(0.15) : appBackgroundColor)
                .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                    Button(role: .destructive) {
                        conversationManager.deleteConversation(withId: conversation.id)
                        if selectedConversation == conversation {
                            selectedConversation = conversationManager.conversations.first
                        }
                    } label: {
                        Label("Delete", systemImage: "trash.fill")
                    }
                    .tint(.red) // Keep delete action red for standard UX
                }
                .swipeActions(edge: .leading, allowsFullSwipe: false) {
                    Button {
                        // TODO: Implement rename functionality
                        print("Rename \(conversation.title)")
                    } label: {
                        Label("Rename", systemImage: "pencil")
                    }
                    .tint(appPrimaryFontColor.opacity(0.8)) // Use app color for rename
                }
            }
        }
        .listStyle(.plain) // Use plain list style for better background color control
        .background(appBackgroundColor) // Ensure list background is correct
        .scrollContentBackground(.hidden) // Allows List background to show through
    }

    private var footer: some View {
        VStack(spacing: 0) {
            Button(action: {
                showingSettings = true
                if horizontalSizeClass == .compact {
                    showingSidebar = false // Close sidebar when opening settings in compact mode
                }
            }) {
                HStack(spacing: 8) {
                    Image(systemName: "gearshape.fill")
                        .font(.system(size: 18))
                    Text("Settings")
                        .font(.headline)
                }
                .padding()
                .frame(height: 44) // Match input bar height
                .frame(maxWidth: .infinity, alignment: .center)
                .foregroundColor(.white)
                .background(appPrimaryFontColor)
                .cornerRadius(10)
                .padding(.horizontal, 16)
                .padding(.bottom, 16)
            }
            .buttonStyle(.plain) // Use plain button style to avoid default button styling
        }
        .background(appBackgroundColor) // Ensure footer has the correct background
    }
}

struct NewConversationSheetView: View {
    @Binding var isPresented: Bool
    var onCreate: (String) -> Void
    @State private var conversationTitle: String = ""
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("New Conversation").foregroundColor(appPrimaryFontColor.opacity(0.8))) {
                    TextField("Enter title (or leave blank)", text: $conversationTitle)
                        .foregroundColor(appPrimaryFontColor)
                }
                
                Button("Create") {
                    onCreate(conversationTitle.isEmpty ? "New Chat" : conversationTitle)
                    isPresented = false
                }
                .foregroundColor(appPrimaryFontColor)
                
                Button("Cancel") {
                    isPresented = false
                }
                .foregroundColor(.red) // Keep cancel red for standard UX
            }
            .navigationTitle("Start New Chat")
            .navigationBarTitleDisplayMode(.inline)
            .background(appBackgroundColor.edgesIgnoringSafeArea(.all)) // Background for the form
            .scrollContentBackground(.hidden) // Make form background transparent
        }
        .frame(minWidth: horizontalSizeClass == .regular ? 400 : nil,
               minHeight: horizontalSizeClass == .regular ? 300 : nil)
        .presentationDetents([.medium, .large])
    }
}

extension Conversation: Hashable {
    public func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
}
