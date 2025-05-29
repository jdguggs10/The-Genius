//
//  ContentView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI
import PhotosUI

struct ContentView: View {
    @StateObject private var conversationManager = ConversationManager()
    @StateObject private var viewModel = ChatViewModel()
    @State private var showingPhotoPicker = false
    @State private var selectedPhotos: [PhotosPickerItem] = []
    @State private var showingSettings = false
    @State private var showingSidebar = false
    @State private var selectedConversation: Conversation?
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        ZStack(alignment: .leading) {
            // Main chat view
            mainChatView
                .offset(x: showingSidebar ? 280 : 0)
                .animation(.easeInOut(duration: 0.3), value: showingSidebar)
            
            // Sidebar overlay
            if showingSidebar {
                // Dark overlay
                Color.black.opacity(0.3)
                    .ignoresSafeArea()
                    .onTapGesture {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            showingSidebar = false
                        }
                    }
                    .offset(x: 280)
                
                // Sidebar
                SidebarView(
                    conversationManager: conversationManager,
                    selectedConversation: $selectedConversation,
                    showingSidebar: $showingSidebar,
                    showingSettings: $showingSettings
                )
                .transition(.move(edge: .leading))
            }
        }
        .onAppear {
            setupViewModel()
        }
        .onChange(of: selectedConversation) { oldValue, newValue in
            if let conversation = newValue {
                viewModel.loadConversation(for: conversation.id)
            }
        }
        .photosPicker(
            isPresented: $showingPhotoPicker,
            selection: $selectedPhotos,
            maxSelectionCount: 5,
            matching: .images
        )
        .sheet(isPresented: $showingSettings) {
            SettingsView()
        }
        .onChange(of: selectedPhotos) { oldPhotos, newPhotos in
            Task {
                viewModel.draftAttachmentData.removeAll()
                for item in newPhotos {
                    if let data = try? await item.loadTransferable(type: Data.self) {
                        viewModel.draftAttachmentData.append(data)
                    }
                }
                selectedPhotos.removeAll()
            }
        }
    }
    
    private func setupViewModel() {
        viewModel.setConversationManager(conversationManager)
        selectedConversation = conversationManager.currentConversation
        viewModel.loadConversation(for: conversationManager.currentConversationId)
    }
    
    private var mainChatView: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Error Message Display
                if let errorMessage = viewModel.currentErrorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .padding()
                        .background(Color.red.opacity(0.1))
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                        .frame(maxWidth: .infinity)
                        .transition(.opacity.combined(with: .move(edge: .top)))
                        .onTapGesture {
                            withAnimation {
                                viewModel.currentErrorMessage = nil
                            }
                        }
                }
                
                // Messages list
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            ForEach(viewModel.messages) { message in
                                MessageBubble(message: message)
                                    .id(message.id)
                            }
                        }
                        .padding(.bottom, 20)
                        .padding(.horizontal, 16)
                    }
                    .onChange(of: viewModel.messages.count) { oldCount, newCount in
                        if let lastMessage = viewModel.messages.last {
                            withAnimation {
                                proxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                }
                
                // Input area
                inputBar
            }
            .navigationTitle(selectedConversation?.title ?? "Fantasy Genius")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                // New message button
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        let newConversation = conversationManager.createNewConversation()
                        selectedConversation = newConversation
                    }) {
                        Image(systemName: "square.and.pencil")
                            .font(.system(size: 16, weight: .medium))
                    }
                    .accessibilityLabel("New conversation")
                    .accessibilityHint("Creates a new conversation")
                }
                
                // Hamburger menu button
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            showingSidebar.toggle()
                        }
                    }) {
                        Image(systemName: "line.horizontal.3")
                    }
                }
            }
        }
        .padding(.horizontal, 0)
        .padding(.vertical, 0)
        .background(Color(.systemBackground))
    }
    
    private var inputBar: some View {
        VStack(spacing: 0) {
            // Divider line above input
            Divider()
                .background(Color(.systemGray4))
            
            HStack(spacing: 12) {
                // Files/attachment button on the left
                Button(action: {
                    isInputFocused = false
                    showingPhotoPicker = true
                }) {
                    Image(systemName: "plus.circle.fill")
                        .font(.title2)
                        .foregroundColor(.primary)
                }
                .frame(width: 32, height: 32)
                
                // Main input container
                HStack(spacing: 8) {
                    // Text input field
                    TextField("Ask anything", text: $viewModel.currentInput, axis: .vertical)
                        .textFieldStyle(.plain)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 12)
                        .font(.system(size: 16))
                        .lineLimit(1...6)
                        .focused($isInputFocused)
                        .onSubmit {
                            if !viewModel.currentInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                                viewModel.sendMessage()
                            }
                        }
                    
                    // Send button (inside the input field)
                    if viewModel.isLoading {
                        ProgressView()
                            .scaleEffect(0.8)
                            .frame(width: 32, height: 32)
                            .padding(.trailing, 8)
                    } else if !viewModel.currentInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || !viewModel.draftAttachmentData.isEmpty {
                        Button(action: {
                            viewModel.sendMessage()
                        }) {
                            Image(systemName: "arrow.up")
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.white)
                                .frame(width: 28, height: 28)
                                .background(Color.blue)
                                .clipShape(Circle())
                        }
                        .padding(.trailing, 8)
                    }
                }
                .background(
                    RoundedRectangle(cornerRadius: 24)
                        .fill(Color(.systemGray6))
                        .overlay(
                            RoundedRectangle(cornerRadius: 24)
                                .stroke(Color(.systemGray4), lineWidth: 0.5)
                        )
                        .shadow(color: Color.black.opacity(0.05), radius: 2, x: 0, y: 1)
                )
                
                // Voice button on the right
                Button(action: {
                    // TODO: Voice input action
                }) {
                    Image(systemName: "mic.fill")
                        .font(.title2)
                        .foregroundColor(.gray) // Gray since not implemented yet
                }
                .frame(width: 32, height: 32)
                .disabled(true) // Disabled for now
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color(.systemBackground))
            .shadow(color: Color.black.opacity(0.1), radius: 4, x: 0, y: -2)
        }
    }
}

#Preview {
    ContentView()
}
