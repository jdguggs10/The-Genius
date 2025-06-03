//
//  ContentView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI
import PhotosUI

struct ContentView: View {
    @EnvironmentObject var conversationManager: ConversationManager
    @StateObject private var viewModel = ChatViewModel()
    @State private var showingPhotoPicker = false
    @State private var selectedPhotos: [PhotosPickerItem] = []

    // State for controlling Settings presentation
    @State private var sidebarRequestsSettings: Bool = false // Triggered by SidebarView
    @State private var showingSettingsSheet: Bool = false    // For sheet presentation in compact
    @State private var showSettingsInDetailView: Bool = false // For detail view presentation in regular

    @State private var showingSidebarForCompact: Bool = false // Explicitly for compact layout's slide-out sidebar
    @State private var selectedConversation: Conversation?
    @FocusState private var isInputFocused: Bool
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @State private var sidebarWidth: CGFloat = 280 // Default width
    @State private var columnVisibility: NavigationSplitViewVisibility = .automatic


    var body: some View {
        GeometryReader { geometry in
            Group { // Group to switch layouts
                if horizontalSizeClass == .compact {
                    compactLayout(geometry: geometry)
                } else {
                    regularLayout(geometry: geometry)
                }
            }
            .onAppear {
                commonOnAppearSetup(geometry: geometry)
            }
            .onChange(of: geometry.size) { oldSize, newSize in
                updateSidebarWidth(for: newSize)
            }
            .onChange(of: horizontalSizeClass) { oldSize, newSize in
                 updateLayoutForSizeClassChange(newSizeClass: newSize, geometry: geometry)
            }
            .onChange(of: selectedConversation) { oldValue, newValue in
                handleSelectedConversationChange(newValue)
            }
            .onChange(of: sidebarRequestsSettings) { oldValue, newValue in
                handleSidebarRequestsSettingsChange(newValue)
            }
            .photosPicker(
                isPresented: $showingPhotoPicker,
                selection: $selectedPhotos,
                maxSelectionCount: 5,
                matching: .images
            )
            .sheet(isPresented: $showingSettingsSheet) { // Sheet for settings in compact view
                SettingsView(isPresented: $showingSettingsSheet)
            }
            .onChange(of: selectedPhotos) { oldPhotos, newPhotos in
                Task {
                    await handlePhotoSelection(newPhotos: newPhotos)
                }
            }
            .onChange(of: conversationManager.conversations) { oldConversations, newConversations in
                // Handle when conversations are loaded asynchronously
                if oldConversations.isEmpty && !newConversations.isEmpty {
                    setupInitialConversationSelection()
                }
            }
        }
    }

    // MARK: - Layouts
    private func compactLayout(geometry: GeometryProxy) -> some View {
        ZStack(alignment: .leading) {
            detailContentNavigationStack() // Main content (chat or placeholder)
                .offset(x: showingSidebarForCompact ? sidebarWidth : 0)
                .animation(.easeInOut(duration: 0.3), value: showingSidebarForCompact)

            if showingSidebarForCompact {
                Color.black.opacity(0.4)
                    .ignoresSafeArea()
                    .onTapGesture {
                        withAnimation(.easeInOut(duration: 0.3)) {
                            showingSidebarForCompact = false
                        }
                    }
                    .zIndex(1) 

                SidebarView(
                    conversationManager: conversationManager,
                    selectedConversation: $selectedConversation,
                    showingSidebar: $showingSidebarForCompact, // For compact mode, this controls the slide-out
                    showingSettings: $sidebarRequestsSettings 
                )
                .frame(width: sidebarWidth)
                .transition(.move(edge: .leading))
                .zIndex(2) 
            }
        }
    }

    private func regularLayout(geometry: GeometryProxy) -> some View {
        NavigationSplitView(columnVisibility: $columnVisibility) {
            SidebarView(
                conversationManager: conversationManager,
                selectedConversation: $selectedConversation,
                // In regular, showingSidebar is always true for the split view column,
                // but we pass a binding that SidebarView might use internally if needed.
                // For this setup, it's more about `sidebarRequestsSettings`.
                showingSidebar: .constant(true), 
                showingSettings: $sidebarRequestsSettings 
            )
            .frame(minWidth: sidebarWidth * 0.8, idealWidth: sidebarWidth, maxWidth: sidebarWidth * 1.2)
        } detail: {
            detailContentNavigationStack()
        }
    }
    
    // MARK: - Detail Content View Builder
    @ViewBuilder
    private func detailContentNavigationStack() -> some View {
        NavigationStack {
            if showSettingsInDetailView && horizontalSizeClass == .regular {
                SettingsView(isPresented: $showSettingsInDetailView)
            } else if let conversation = selectedConversation {
                chatContentView(for: conversation)
            } else {
                // Placeholder when no conversation is selected and not showing settings
                Text("Select a conversation or start a new one.")
                    .font(.title)
                    .foregroundColor(.secondary)
                    .navigationTitle("Fantasy Genius")
                    .toolbar(content: navigationToolbarContent)
            }
        }
        .background(Color(.systemBackground))
    }

    // MARK: - Chat Content
    private func chatContentView(for conversation: Conversation) -> some View {
        VStack(spacing: 0) {
            if let errorMessage = viewModel.currentErrorMessage {
                Text(errorMessage)
                    .foregroundColor(.red)
                    .padding()
                    .background(Color.red.opacity(0.1))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    .frame(maxWidth: .infinity)
                    .transition(.opacity.combined(with: .move(edge: .top)))
                    .onTapGesture { withAnimation { viewModel.currentErrorMessage = nil } }
            }
            GeometryReader { listGeometry in
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            ForEach(viewModel.messages) { message in
                                MessageBubble(message: message)
                                    .id(message.id)
                                    .padding(.horizontal, horizontalSizeClass == .regular ? max(32, listGeometry.safeAreaInsets.leading + 16) : 16)
                            }
                            
                            // Display status message here, below messages but in scroll view
                            if let status = viewModel.statusMessage, viewModel.isLoading {
                                HStack {
                                    Spacer()
                                    Text(status)
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                        .padding(.vertical, 5)
                                        .padding(.horizontal, 10)
                                        .background(Color(.systemGray5))
                                        .clipShape(Capsule())
                                    Spacer()
                                }
                                .padding(.horizontal, horizontalSizeClass == .regular ? max(32, listGeometry.safeAreaInsets.leading + 16) : 16)
                                .padding(.top, 5) // Add some spacing from the last message
                                .id("statusMessageView") // Give it an ID to scroll to if needed
                            }
                        }
                        .padding(.vertical, 10)
                        .onChange(of: viewModel.messages.count) { _, newCount in
                            // Debounce scroll to avoid conflicts during rapid updates
                            Task { @MainActor in
                                try? await Task.sleep(nanoseconds: 50_000_000) // 50ms debounce
                                if let lastMessage = viewModel.messages.last {
                                    withAnimation(.easeOut(duration: 0.3)) { 
                                        proxy.scrollTo(lastMessage.id, anchor: .bottom) 
                                    }
                                }
                            }
                        }
                        // Consolidated status message handling to prevent scroll conflicts
                        .onChange(of: viewModel.statusMessage) { oldStatus, newStatus in
                            // Only scroll for status changes if not also scrolling for message updates
                            Task { @MainActor in
                                try? await Task.sleep(nanoseconds: 100_000_000) // 100ms debounce
                                
                                if newStatus != nil && viewModel.isLoading && viewModel.streamingText.isEmpty {
                                    withAnimation(.easeOut(duration: 0.3)) { 
                                        proxy.scrollTo("statusMessageView", anchor: .bottom) 
                                    }
                                } else if oldStatus != nil && newStatus == nil && viewModel.streamingText.isEmpty {
                                    if let lastMessage = viewModel.messages.last {
                                        withAnimation(.easeOut(duration: 0.3)) { 
                                            proxy.scrollTo(lastMessage.id, anchor: .bottom) 
                                        }
                                    }
                                }
                            }
                        }
                        .onTapGesture { isInputFocused = false } // Dismiss keyboard
                    }
                }
            }
            inputBar
        }
        .navigationTitle(conversation.title)
        .navigationBarTitleDisplayMode(horizontalSizeClass == .regular ? .automatic : .inline)
        .toolbar(content: navigationToolbarContent)
    }

    // MARK: - Input Bar
    private var inputBar: some View {
         VStack(spacing: 0) {
            if !viewModel.draftAttachmentData.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(viewModel.draftAttachmentData.indices, id: \.self) { index in
                            ZStack(alignment: .topTrailing) {
                                if let uiImage = UIImage(data: viewModel.draftAttachmentData[index]) {
                                    Image(uiImage: uiImage).resizable().scaledToFill()
                                        .frame(width: 60, height: 60).clipShape(RoundedRectangle(cornerRadius: 8))
                                        .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.gray.opacity(0.5), lineWidth: 1))
                                } else {
                                    Rectangle().fill(Color.gray.opacity(0.3)).frame(width: 60, height: 60).cornerRadius(8)
                                        .overlay(Image(systemName: "exclamationmark.triangle").foregroundColor(.white))
                                }
                                Button(action: { viewModel.draftAttachmentData.remove(at: index) }) {
                                    Image(systemName: "xmark.circle.fill").foregroundColor(.gray)
                                        .background(Color.white.opacity(0.7)).clipShape(Circle())
                                }.padding(4)
                            }
                        }
                    }
                    .padding(.horizontal, horizontalSizeClass == .regular ? 20 : 12).padding(.top, 8)
                }.frame(height: 70).transition(.opacity.combined(with: .scale(scale: 0.8, anchor: .bottom)))
                Divider().padding(.top, 4)
            }
            HStack(alignment: .bottom, spacing: horizontalSizeClass == .regular ? 16 : 10) {
                Button(action: { isInputFocused = false; showingPhotoPicker = true }) {
                    Image(systemName: "plus.circle.fill").font(.system(size: 24)).foregroundColor(.accentColor)
                }.frame(minWidth: 44, minHeight: 44).padding(.bottom, 5)
                HStack(alignment: .bottom, spacing: 8) {
                    TextField("Ask anything", text: $viewModel.currentInput, axis: .vertical)
                        .textFieldStyle(.plain).padding(.horizontal, 12).padding(.vertical, 10)
                        .font(.system(size: 17)).lineLimit(1...5).focused($isInputFocused)
                        .onSubmit { if !viewModel.currentInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { viewModel.sendMessage() } }
                        .frame(minHeight: 44)
                    if viewModel.isLoading {
                        ProgressView().scaleEffect(0.9).frame(width: 30, height: 30).padding(.trailing, 6).padding(.bottom, 7)
                    } else if !viewModel.currentInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || !viewModel.draftAttachmentData.isEmpty {
                        Button(action: { viewModel.sendMessage() }) {
                            Image(systemName: "arrow.up.circle.fill").font(.system(size: 28)).foregroundColor(.accentColor)
                        }.frame(minWidth: 44, minHeight: 44).padding(.trailing, 4).padding(.bottom, 3)
                    }
                }.background(RoundedRectangle(cornerRadius: 22).fill(Color(.systemGray6)))
                Button(action: { /* TODO: Voice input */ }) {
                    Image(systemName: "mic.fill").font(.system(size: 24)).foregroundColor(.gray)
                }.frame(minWidth: 44, minHeight: 44).padding(.bottom, 5).disabled(true)
            }
            .padding(.horizontal, horizontalSizeClass == .regular ? 20 : 12).padding(.top, 8)
            .padding(.bottom, UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }.first?.windows.first?.safeAreaInsets.bottom ?? 10)
            .background(Color(.systemBackground))
        }.frame(maxWidth: .infinity).animation(.spring(), value: viewModel.draftAttachmentData.isEmpty)
    }
    
    // MARK: - Toolbar Content
    @ToolbarContentBuilder
    private func navigationToolbarContent() -> some ToolbarContent {
        ToolbarItem(placement: .navigationBarTrailing) {
            Menu {
                Button(action: {
                    showSettingsInDetailView = false // Ensure settings detail is dismissed if open
                    viewModel.startNewConversation()
                    selectedConversation = conversationManager.conversations.first
                    if horizontalSizeClass == .compact { withAnimation { showingSidebarForCompact = false } }
                }) {
                    Label("New Conversation", systemImage: "square.and.pencil")
                }
                
                if selectedConversation != nil {
                    Button(action: {
                        viewModel.resetConversationContext()
                    }) {
                        Label("Reset Context", systemImage: "arrow.clockwise")
                    }
                }
            } label: {
                Image(systemName: "ellipsis.circle")
                    .font(.system(size: 17, weight: .semibold))
                    .frame(minWidth: 44, minHeight: 44)
            }
            .accessibilityLabel("Conversation options")
        }
        
        if horizontalSizeClass == .compact {
            ToolbarItem(placement: .navigationBarLeading) {
                Button(action: { withAnimation(.easeInOut(duration: 0.3)) { showingSidebarForCompact.toggle() } }) {
                    Image(systemName: "line.horizontal.3").font(.system(size: 17, weight: .semibold))
                        .frame(minWidth: 44, minHeight: 44)
                }
                .accessibilityLabel("Toggle sidebar")
            }
        }
    }

    // MARK: - Helper Functions
    private func commonOnAppearSetup(geometry: GeometryProxy) {
        setupViewModelInitialLoad()
        // Check if conversations are already loaded (in case this is called after async loading completes)
        if !conversationManager.conversations.isEmpty {
            setupInitialConversationSelection()
        }
        updateSidebarWidth(for: geometry.size)
    }

    private func updateSidebarWidth(for size: CGSize) {
        if horizontalSizeClass == .regular { 
            sidebarWidth = min(max(size.width * 0.33, 300), 320) // Slightly narrower max for regular
        } else { 
            sidebarWidth = max(size.width * 0.75, 260) 
        }
    }
    
    private func updateLayoutForSizeClassChange(newSizeClass: UserInterfaceSizeClass?, geometry: GeometryProxy) {
        if newSizeClass == .regular {
            // Transitioning to Regular:
            // Sidebar is now part of NavigationSplitView, so `showingSidebarForCompact` is irrelevant for layout.
            // If settings were shown via sheet (compact), transition to detail view.
            if showingSettingsSheet {
                showingSettingsSheet = false // Close sheet
                showSettingsInDetailView = true // Show in detail
                selectedConversation = nil // Ensure chat is not displayed behind settings
            }
        } else { // Transitioning to Compact:
            // Sidebar is now manually controlled by `showingSidebarForCompact`.
            showingSidebarForCompact = false // Default to hidden on switch to compact.
            // If settings were shown in detail view (regular), transition to sheet.
            if showSettingsInDetailView {
                showSettingsInDetailView = false // Hide from detail
                showingSettingsSheet = true    // Show as sheet
            }
        }
        updateSidebarWidth(for: geometry.size)
    }
    
    private func handleSelectedConversationChange(_ newConversation: Conversation?) {
        if newConversation != nil {
            showSettingsInDetailView = false // Selecting a conversation hides settings
            if let conversation = newConversation {
                viewModel.loadConversation(for: conversation.id)
            }
        }
        if horizontalSizeClass == .compact && newConversation != nil {
            withAnimation { showingSidebarForCompact = false }
        }
    }

    private func handleSidebarRequestsSettingsChange(_ requestsSettings: Bool) {
        if requestsSettings {
            if horizontalSizeClass == .compact {
                showingSettingsSheet = true
            } else { // Regular
                selectedConversation = nil // Deselect conversation to show settings in detail
                showSettingsInDetailView = true
            }
            sidebarRequestsSettings = false // Reset trigger
        }
    }
    
    private func setupViewModelInitialLoad() {
        viewModel.setConversationManager(conversationManager)
        // Since conversations are loading asynchronously, we need to be more careful here
        // The async loading will trigger view updates when conversations are loaded
    }
    
    private func setupInitialConversationSelection() {
        // This function handles conversation selection once conversations are loaded
        if !showSettingsInDetailView && selectedConversation == nil {
            if conversationManager.conversations.isEmpty {
                selectedConversation = conversationManager.createNewConversation()
            } else {
                selectedConversation = conversationManager.conversations.first
            }
        }
        // Load conversation if one is selected (and not showing settings in detail)
        if let conv = selectedConversation, !showSettingsInDetailView {
            viewModel.loadConversation(for: conv.id)
        }
    }

    private func handlePhotoSelection(newPhotos: [PhotosPickerItem]) async {
        // Measure photo processing performance
        let startTime = CFAbsoluteTimeGetCurrent()
        await self.processPhotosAsync(newPhotos: newPhotos)
        let duration = CFAbsoluteTimeGetCurrent() - startTime
        
        if duration > 0.1 { // 100ms threshold
            print("Photo processing took \(String(format: "%.3f", duration))s - exceeds threshold")
        }
    }
    
    // Extract the async photo processing logic into a separate method
    private func processPhotosAsync(newPhotos: [PhotosPickerItem]) async {
        viewModel.draftAttachmentData.removeAll()

        for item in newPhotos {
            do {
                if let data = try await item.loadTransferable(type: Data.self) {
                    // Limit image size to prevent memory issues
                    if let processedData = await processImageData(data) {
                        await MainActor.run {
                            viewModel.draftAttachmentData.append(processedData)
                        }
                    }
                }
            } catch {
                print("Failed to load photo: \(error)")
            }
        }

        await MainActor.run {
            selectedPhotos.removeAll()
        }
    }
    
    // Process and resize images to prevent memory hangs
    private func processImageData(_ data: Data) async -> Data? {
        return await withTaskGroup(of: Data?.self) { group in
            group.addTask {
                autoreleasepool {
                    guard let image = UIImage(data: data) else { return nil }
                    
                    // Resize large images to reasonable size (max 1024px)
                    let maxDimension: CGFloat = 1024
                    let scale = min(maxDimension / image.size.width, maxDimension / image.size.height, 1.0)
                    
                    if scale < 1.0 {
                        let newSize = CGSize(
                            width: image.size.width * scale,
                            height: image.size.height * scale
                        )
                        
                        UIGraphicsBeginImageContextWithOptions(newSize, false, 0.0)
                        defer { UIGraphicsEndImageContext() }
                        
                        image.draw(in: CGRect(origin: .zero, size: newSize))
                        
                        if let resizedImage = UIGraphicsGetImageFromCurrentImageContext(),
                           let compressedData = resizedImage.jpegData(compressionQuality: 0.8) {
                            return compressedData
                        }
                    }
                    
                    // Return original data if no resizing needed or if resizing failed
                    return data
                }
            }
            
            for await result in group {
                if let processedData = result {
                    return processedData
                }
            }
            return nil
        }
    }
}
