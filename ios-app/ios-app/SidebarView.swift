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

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            
            conversationList
            
            Spacer() // Pushes everything above it up
            
            footer // Settings button
        }
        .background(appBackgroundColor)
        .edgesIgnoringSafeArea(.bottom) // Extend background to bottom edge
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .sheet(isPresented: $showingNewConversationSheet) {
            NewConversationSheetView(isPresented: $showingNewConversationSheet) { newTitle in
                let conversation = conversationManager.createNewConversation(title: newTitle)
                selectedConversation = conversation // Select the new conversation
                if horizontalSizeClass == .compact {
                    showingSidebar = false // Close sidebar in compact mode after creation
                }
            }
        }
    }

    private var header: some View {
        HStack {
            Text("Conversations")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(appPrimaryFontColor)
            Spacer()
            Button(action: {
                showingNewConversationSheet = true
            }) {
                Image(systemName: "square.and.pencil")
                    .font(.title2)
                    .foregroundColor(appPrimaryFontColor)
            }
            .buttonStyle(.plain)
            .padding(.trailing, 8)
        }
        .padding()
        .background(appBackgroundColor) // Ensure header has the correct background
    }

    private var conversationList: some View {
        List(selection: $selectedConversation) {
            ForEach(conversationManager.conversations) { conversation in
                NavigationLink(value: conversation) {
                    Text(conversation.title)
                        .foregroundColor(appPrimaryFontColor) // Font color for conversation titles
                }
                .listRowBackground(selectedConversation == conversation ? appPrimaryFontColor.opacity(0.15) : appBackgroundColor)
                .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                    Button(role: .destructive) {
                        conversationManager.deleteConversation(conversation.id)
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
            Divider().background(appPrimaryFontColor.opacity(0.2))
            
            Button(action: {
                showingSettings = true
                if horizontalSizeClass == .compact {
                    showingSidebar = false // Close sidebar when opening settings in compact mode
                }
            }) {
                HStack {
                    Image(systemName: "gearshape.fill") // SF Symbol for settings
                        .font(.title3)
                    Text("Settings")
                        .font(.headline)
                    Spacer()
                }
                .padding()
                .foregroundColor(appPrimaryFontColor)
                .contentShape(Rectangle()) // Makes the whole HStack tappable
            }
            .buttonStyle(.plain) // Use plain button style
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

struct SidebarView_Previews: PreviewProvider {
    static var previews: some View {
        // Create a dummy ConversationManager for preview
        let manager = ConversationManager()
        let _ = manager.createNewConversation(title: "General Discussion")
        let _ = manager.createNewConversation(title: "SwiftUI Tips")
        
        // Using @State for selectedConversation in Preview
        @State var selectedConv: Conversation? = manager.conversations.first
        @State var showingSidebar: Bool = true
        @State var showingSettings: Bool = false

        return Group {
            SidebarView(
                conversationManager: manager,
                selectedConversation: $selectedConv,
                showingSidebar: $showingSidebar,
                showingSettings: $showingSettings
            )
            .environmentObject(manager) // Provide the manager as an environment object
            .previewDisplayName("Sidebar Light")

            SidebarView(
                conversationManager: manager,
                selectedConversation: $selectedConv,
                showingSidebar: $showingSidebar,
                showingSettings: $showingSettings
            )
            .environmentObject(manager)
            .preferredColorScheme(.dark) // Example of dark mode (colors will adapt if semantic)
            .previewDisplayName("Sidebar Dark (for reference)")
            
            NewConversationSheetView(isPresented: .constant(true), onCreate: { _ in })
                .previewDisplayName("New Conversation Sheet")
        }
    }
} 