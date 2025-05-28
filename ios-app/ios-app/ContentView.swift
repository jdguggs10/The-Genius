//
//  ContentView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI
import PhotosUI

struct ContentView: View {
    @StateObject private var viewModel = ChatViewModel()
    @State private var showingPhotoPicker = false
    @State private var selectedPhotos: [PhotosPickerItem] = []
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Messages list
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            ForEach(viewModel.messages) { message in
                                MessageBubble(message: message)
                                    .id(message.id)
                            }
                        }
                    }
                    .onChange(of: viewModel.messages.count) { oldCount, newCount in
                        // Auto-scroll to bottom when new message appears
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
            .navigationTitle("AI Assistant")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                // Settings button
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        // Settings action - we'll implement this later
                    }) {
                        Image(systemName: "gearshape")
                    }
                }
                
                // Archive button
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        // Archive action - we'll implement this later
                    }) {
                        Image(systemName: "line.horizontal.3")
                    }
                }
            }
        }
        .photosPicker(
            isPresented: $showingPhotoPicker,
            selection: $selectedPhotos,
            maxSelectionCount: 5,
            matching: .images
        )
        .onChange(of: selectedPhotos) { oldItems, newItems in
            // Handle photo selection
            Task {
                for item in newItems {
                    if let data = try? await item.loadTransferable(type: Data.self) {
                        // We have the data, directly add it to the view model
                        viewModel.draftAttachmentData.append(data)
                    }
                }
                selectedPhotos.removeAll()
            }
        }
        .onAppear {
            viewModel.loadConversation()
        }
        .onDisappear {
            viewModel.saveConversation()
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color(.systemBackground))
    }
    
    private var inputBar: some View {
        HStack(spacing: 8) {
            // Mic button (we'll implement voice later)
            Button(action: {
                // Voice input action
            }) {
                Image(systemName: "mic.fill")
                    .font(.title2)
                    .foregroundColor(.blue)
            }
            .frame(width: 44, height: 44)
            
            // Attachment button
            Button(action: {
                showingPhotoPicker = true
            }) {
                Image(systemName: "paperclip")
                    .font(.title2)
                    .foregroundColor(.blue)
            }
            .frame(width: 44, height: 44)
            
            // Text input
            TextField("Type a message...", text: $viewModel.currentInput, axis: .vertical)
                .textFieldStyle(.roundedBorder)
                .lineLimit(1...5)
                .focused($isInputFocused)
                .onSubmit {
                    viewModel.sendMessage()
                }
            
            // Send button
            Button(action: {
                viewModel.sendMessage()
            }) {
                Image(systemName: "paperplane.fill")
                    .font(.title2)
                    .foregroundColor(viewModel.currentInput.isEmpty ? .gray : .blue)
            }
            .frame(width: 44, height: 44)
            .disabled(viewModel.currentInput.isEmpty || viewModel.isLoading)
        }
    }
}

#Preview {
    ContentView()
}
