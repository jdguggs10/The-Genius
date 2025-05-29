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
    @State private var showingSettings = false
    @FocusState private var isInputFocused: Bool
    
    var body: some View {
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
                                viewModel.currentErrorMessage = nil // Tap to dismiss
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
                        // Add some bottom padding to ensure last message is well above input bar
                        .padding(.bottom, 10)
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
            .navigationTitle("Fantasy Genius")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                // Settings button
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingSettings = true
                    }) {
                        Image(systemName: "gearshape")
                    }
                }
                
                // Archive button (Example - can be removed or repurposed)
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        // Archive action - implement later
                    }) {
                        Image(systemName: "line.horizontal.3")
                    }
                }
            }
        }
        .photosPicker(
            isPresented: $showingPhotoPicker,
            selection: $selectedPhotos,
            maxSelectionCount: 5, // Allow up to 5 images for now
            matching: .images
        )
        .sheet(isPresented: $showingSettings) {
            SettingsView()
        }
        .onChange(of: selectedPhotos) { oldItems, newItems in
            Task {
                viewModel.draftAttachmentData.removeAll() // Clear previous drafts
                for item in newItems {
                    if let data = try? await item.loadTransferable(type: Data.self) {
                        viewModel.draftAttachmentData.append(data)
                    }
                }
                selectedPhotos.removeAll() // Clear picker selection
            }
        }
        .onAppear {
            viewModel.loadConversation()
        }
        // .onDisappear {
        //     viewModel.saveConversation() // Saving on disappear might be too frequent or interruptive
        // }
        // Consider saving explicitly or on app lifecycle events like scenePhase changes.
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Color(.systemGroupedBackground)) // Use a grouped background for better contrast
    }
    
    private var inputBar: some View {
        HStack(spacing: 8) {
            // Mic button (Placeholder)
            Button(action: {
                // TODO: Voice input action
            }) {
                Image(systemName: "mic.fill")
                    .font(.title2)
                    .foregroundColor(.gray) // Changed to gray as it's not implemented
            }
            .frame(width: 44, height: 44)
            .disabled(true) // Disabled for now
            
            // Attachment button
            Button(action: {
                isInputFocused = false // Dismiss keyboard before showing picker
                showingPhotoPicker = true
            }) {
                Image(systemName: "paperclip")
                    .font(.title2)
                    .foregroundColor(.blue)
            }
            .frame(width: 44, height: 44)
            
            // Text input
            TextField("Ask Fantasy Genius...", text: $viewModel.currentInput, axis: .vertical)
                .textFieldStyle(.plain)
                .padding(.horizontal, 12)
                .padding(.vertical, 10)
                .background(Color(.systemGray6))
                .clipShape(RoundedRectangle(cornerRadius: 20))
                .lineLimit(1...5)
                .focused($isInputFocused)
                .onSubmit {
                    if !viewModel.currentInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        viewModel.sendMessage()
                    }
                }
            
            // Send button
            if viewModel.isLoading {
                ProgressView()
                    .frame(width: 44, height: 44)
            } else {
                Button(action: {
                    viewModel.sendMessage()
                }) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.title)
                        .foregroundColor(viewModel.currentInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && viewModel.draftAttachmentData.isEmpty ? .gray : .blue)
                }
                .frame(width: 44, height: 44)
                .disabled(viewModel.currentInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && viewModel.draftAttachmentData.isEmpty)
            }
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 4)
    }
}

#Preview {
    ContentView()
}
