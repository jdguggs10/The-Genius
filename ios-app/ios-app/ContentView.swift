//
//  ContentView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI
import PhotosUI
import UIKit

private let appBackgroundColor = Color(red: 253/255, green: 245/255, blue: 230/255) // FDF5E6
private let appPrimaryFontColor = Color(red: 61/255, green: 108/255, blue: 104/255) // 3D6C68

struct ContentView: View {
    @EnvironmentObject var conversationManager: ConversationManager
    @StateObject private var viewModel = ChatViewModel()
    @State private var showingPhotoPicker = false
    @State private var selectedPhotos: [PhotosPickerItem] = []
    
    // Local state for message input
    @State private var messageInput: String = ""

    // State for controlling Settings presentation
    @State private var sidebarRequestsSettings: Bool = false // Triggered by SidebarView
    @State private var showingSettingsSheet: Bool = false    // For sheet presentation in compact
    @State private var showSettingsInDetailView: Bool = false // For detail view presentation in regular

    @State private var showingSidebarForCompact: Bool = false // Explicitly for compact layout's slide-out sidebar
    @State private var selectedConversation: Conversation?
    @FocusState private var isInputFocused: Bool
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @State private var sidebarWidth: CGFloat = 280 // Default width
    @State private var columnVisibility: NavigationSplitViewVisibility = .all

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
                // Focus text input on app launch for instant keyboard
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    isInputFocused = true
                }
            }
            .onChange(of: geometry.size) { oldSize, newSize in
                updateSidebarWidth(for: newSize)
            }
            .onChange(of: horizontalSizeClass) { oldSize, newSize in
                 updateLayoutForSizeClassChange(newSizeClass: newSize, geometry: geometry)
            }
            .onChange(of: selectedConversation) { oldValue, newValue in
                handleSelectedConversationChange(oldValue, newValue)
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
            // Add lifecycle event handlers
            .onReceive(NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)) { _ in
                // App is going to background - cancel any streaming requests
                viewModel.cancelStreamingRequest()
            }
            .onReceive(NotificationCenter.default.publisher(for: UIApplication.didEnterBackgroundNotification)) { _ in
                // App entered background - ensure streaming is cancelled
                viewModel.cancelStreamingRequest()
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
                SettingsView(
                    isPresented: $showSettingsInDetailView,
                    onDismiss: {
                        // Ensure sidebar stays visible when dismissing settings on iPad
                        if horizontalSizeClass == .regular {
                            columnVisibility = .all
                        }
                    }
                )
            } else if let conversation = selectedConversation {
                chatContentView(for: conversation)
            } else {
                // Placeholder when no conversation is selected and not showing settings
                Text("Select a conversation or start a new one.")
                    .font(.title)
                    .foregroundColor(.primary)
                    .navigationTitle("Fantasy Genius")
                    .toolbar(content: navigationToolbarContent)
                    .safeAreaInset(edge: .top) {
                        // This creates extra space below the navigation bar
                        Color.clear
                            .frame(height: 4)
                    }
            }
        }
        .background(appBackgroundColor)
    }

    // MARK: - Chat Content
    private func chatContentView(for conversation: Conversation) -> some View {
        VStack(spacing: 0) {
            errorMessageView
            messageListView
            inputBarView
        }
        .background(appBackgroundColor)
        .navigationTitle(conversation.title)
        .navigationBarTitleDisplayMode(horizontalSizeClass == .regular ? .automatic : .inline)
        .toolbar(content: navigationToolbarContent)
        .safeAreaInset(edge: .top) {
            // This creates extra space below the navigation bar
            Color.clear
                .frame(height: 4)
        }
    }
    
    // MARK: - Error Message View
    @ViewBuilder
    private var errorMessageView: some View {
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
                        viewModel.clearError()
                    } 
                }
        }
    }
    
    // MARK: - Message List View
    private var messageListView: some View {
        GeometryReader { listGeometry in
            let horizontalInset = horizontalSizeClass == .regular
                ? max(20, listGeometry.safeAreaInsets.leading + 8)
                : 8
            
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 0) {
                        ForEach(viewModel.messages) { message in
                            MessageBubble(message: message)
                                .environmentObject(viewModel)
                                .id(message.id)
                                .padding(.horizontal, horizontalInset)
                        }
                        
                        statusMessageView(horizontalInset: horizontalInset)
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
                }
            }
        }
    }
    
    // MARK: - Status Message View
    @ViewBuilder
    private func statusMessageView(horizontalInset: CGFloat) -> some View {
        if let status = viewModel.statusMessage, viewModel.isLoading {
            HStack {
                Spacer()
                Text(status)
                    .font(.caption)
                    .foregroundColor(appPrimaryFontColor.opacity(0.8))
                    .padding(.vertical, 5)
                    .padding(.horizontal, 10)
                    .background(appPrimaryFontColor.opacity(0.1))
                    .clipShape(Capsule())
                Spacer()
            }
            .padding(.horizontal, horizontalInset)
            .padding(.top, 5)
            .id("statusMessageView")
        }
    }
    
    // MARK: - Input Bar View
    private var inputBarView: some View {
        let hasContent = !messageInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || !viewModel.draftAttachmentData.isEmpty
        let sendButtonColor = hasContent ? appPrimaryFontColor : appPrimaryFontColor.opacity(0.5)
        
        return HStack(alignment: .center, spacing: horizontalSizeClass == .regular ? 8 : 6) {
            photoPickerButton
            messageInputContainer(hasContent: hasContent)
            // Baseball button
            Button(action: {
                // TODO: Handle baseball button action
            }) {
                Image(systemName: "baseball.fill")
                    .font(.system(size: 28))
                    .foregroundColor(appPrimaryFontColor)
            }
            .frame(width: 44, height: 44)
            .buttonStyle(.plain)
            sendButton(hasContent: hasContent, sendButtonColor: sendButtonColor)
            .padding(.trailing, 8)
        }
        .frame(height: 66)
        .background(Color.white)
        .overlay(inputBarBorder)
        .gesture(keyboardDismissGesture)
        .frame(maxWidth: .infinity)
    }
    
    // MARK: - Input Bar Components
    private var photoPickerButton: some View {
        Button(action: {
            isInputFocused = false
            showingPhotoPicker = true
        }) {
            Image(systemName: "plus.circle.fill")
                .font(.system(size: 24))
                .foregroundColor(appPrimaryFontColor)
        }
        .frame(width: 44, height: 44)
        .buttonStyle(.plain)
        .padding(.leading, 8)
    }
    
    private func messageInputContainer(hasContent: Bool) -> some View {
        HStack(spacing: 8) {
            TextField("Ask Genius about...", text: $messageInput)
                .textFieldStyle(.plain)
                .font(.system(size: 17))
                .lineLimit(1)
                .focused($isInputFocused)
                .onSubmit {
                    if hasContent {
                        viewModel.sendMessage(messageInput)
                        messageInput = ""
                    }
                }
        }
        .padding(.horizontal, 12)
        .frame(maxWidth: .infinity)
        .onTapGesture {
            isInputFocused = true
        }
    }
    
    private func sendButton(hasContent: Bool, sendButtonColor: Color) -> some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
                    .scaleEffect(0.8)
            } else {
                Button(action: {
                    if hasContent {
                        viewModel.sendMessage(messageInput)
                        messageInput = ""
                    }
                }) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.system(size: 28))
                        .foregroundColor(sendButtonColor)
                }
                .buttonStyle(.plain)
                .disabled(!hasContent)
            }
        }
        .frame(width: 44, height: 44)
        .padding(.trailing, 8)
    }
    
    private var inputBarBorder: some View {
        VStack(spacing: 0) {
            // Top shading/shadow effect
            Rectangle()
                .fill(
                    LinearGradient(
                        gradient: Gradient(colors: [
                            appPrimaryFontColor.opacity(0.1),
                            Color.clear
                        ]),
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .frame(height: 1)
            
            Spacer()
        }
    }
    
    private var keyboardDismissGesture: some Gesture {
        DragGesture()
            .onEnded { value in
                if value.translation.height > 50 {
                    isInputFocused = false
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
        
        // Apply taller navigation bar appearance to UIKit
        let appearance = UINavigationBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundColor = UIColor(red: 253/255, green: 245/255, blue: 230/255, alpha: 1.0) // Match appBackgroundColor
        appearance.shadowColor = .clear
        
        // Custom height setup
        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance 
        UINavigationBar.appearance().compactAppearance = appearance
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
            // Ensure sidebar is visible by default in regular layout
            columnVisibility = .all
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
    
    private func handleSelectedConversationChange(_ oldValue: Conversation?, _ newValue: Conversation?) {
        // Cancel any streaming request from previous conversation
        if oldValue != nil && oldValue?.id != newValue?.id {
            viewModel.cancelStreamingRequest()
        }
        
        if newValue != nil {
            showSettingsInDetailView = false // Selecting a conversation hides settings
            if let conversation = newValue {
                viewModel.loadConversation(for: conversation.id)
            }
        }
        if horizontalSizeClass == .compact && newValue != nil {
            withAnimation { showingSidebarForCompact = false }
        }
    }

    private func handleSidebarRequestsSettingsChange(_ requestsSettings: Bool) {
        if requestsSettings {
            if horizontalSizeClass == .compact {
                showingSettingsSheet = true
            } else { // Regular
                // Ensure sidebar stays visible when showing settings
                columnVisibility = .all
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
        
        // Create a task we can cancel if needed
        let processingTask = Task {
            await self.processPhotosAsync(newPhotos: newPhotos)
        }
        
        // Set up a timeout to prevent hanging processes
        let timeoutTask = Task {
            try? await Task.sleep(nanoseconds: 10_000_000_000) // 10 second timeout
            if !processingTask.isCancelled {
                print("Photo processing timeout - cancelling task")
                processingTask.cancel()
            }
        }
        
        await processingTask.value
        timeoutTask.cancel() // Cancel the timeout task once processing completes
        
        let duration = CFAbsoluteTimeGetCurrent() - startTime
        if duration > 0.1 { // 100ms threshold
            print("Photo processing took \(String(format: "%.3f", duration))s - exceeds threshold")
        }
    }
    
    // Extract the async photo processing logic into a separate method
    private func processPhotosAsync(newPhotos: [PhotosPickerItem]) async {
        viewModel.draftAttachmentData.removeAll()

        for item in newPhotos {
            // Check for task cancellation
            if Task.isCancelled { break }
            
            do {
                if let data = try await item.loadTransferable(type: Data.self) {
                    // Limit image size to prevent memory issues
                    if let processedData = await processImageData(data) {
                        // Check for task cancellation again
                        if Task.isCancelled { break }
                        
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
                // Check for cancellation at task start
                if Task.isCancelled { return nil }
                
                return autoreleasepool {
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
            
            // Retrieve the first completed task's result (if any) and cancel any remaining tasks
            defer { group.cancelAll() }
            return await group.next() ?? nil
        }
    }

    // MARK: - Toolbar Content
    @ToolbarContentBuilder
    private func navigationToolbarContent() -> some ToolbarContent {
        ToolbarItem(placement: .navigationBarTrailing) {
            Button(action: {
                showSettingsInDetailView = false // Ensure settings detail is dismissed if open
                viewModel.startNewConversation()
                selectedConversation = conversationManager.conversations.first
                if horizontalSizeClass == .compact { withAnimation { showingSidebarForCompact = false } }
            }) {
                Image(systemName: "square.and.pencil")
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundColor(appPrimaryFontColor)
                    .frame(minWidth: 44, minHeight: 44 + 4) // Add 4 points to match taller toolbar
            }
            .accessibilityLabel("New Conversation")
        }
        
        if horizontalSizeClass == .compact {
            ToolbarItem(placement: .navigationBarLeading) {
                Button(action: { withAnimation(.easeInOut(duration: 0.3)) { showingSidebarForCompact.toggle() } }) {
                    Image(systemName: "line.horizontal.3").font(.system(size: 17, weight: .semibold))
                        .foregroundColor(appPrimaryFontColor)
                        .frame(minWidth: 44, minHeight: 44 + 4) // Add 4 points to match taller toolbar
                }
                .accessibilityLabel("Toggle sidebar")
            }
        }
    }
}

// MARK: - Simplified Input Bar Component
struct InputBar: View {
    @Binding var messageInput: String
    @FocusState.Binding var isInputFocused: Bool
    @ObservedObject var viewModel: ChatViewModel
    @Binding var showingPhotoPicker: Bool
    let horizontalSizeClass: UserInterfaceSizeClass?
    
    var body: some View {
        VStack(spacing: 0) {
            // Attachment preview section - isolated to minimize recomposition
            if !viewModel.draftAttachmentData.isEmpty {
                AttachmentPreviewSection(
                    attachmentData: viewModel.draftAttachmentData,
                    onRemove: { index in
                        viewModel.draftAttachmentData.remove(at: index)
                    },
                    horizontalSizeClass: horizontalSizeClass
                )
                
                Divider().padding(.top, 4)
            }
            
            // Main input bar
            VStack(spacing: 0) {
                // Top half - Message input
                HStack {
                    TextField("Ask Genius about...", text: $messageInput)
                        .textFieldStyle(.plain)
                        .font(.system(size: 17))
                        .lineLimit(1)
                        .focused($isInputFocused)
                        .onSubmit {
                            if !messageInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                                viewModel.sendMessage(messageInput)
                                messageInput = ""
                            }
                        }
                    Spacer()
                }
                .padding(.horizontal, 12)
                .frame(height: 44)
                .frame(maxWidth: .infinity)
                .onTapGesture {
                    isInputFocused = true
                }
                
                // Bottom half - Buttons
                HStack(alignment: .center, spacing: horizontalSizeClass == .regular ? 12 : 8) {
                    // Photo picker button
                    Button(action: {
                        isInputFocused = false
                        showingPhotoPicker = true
                    }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(appPrimaryFontColor)
                    }
                    .frame(width: 44, height: 44)
                    .buttonStyle(.plain)
                    
                    Spacer()
                    
                    // Voice input button (disabled)
                    Button(action: { /* TODO: Voice input */ }) {
                        Image(systemName: "mic.fill")
                            .font(.system(size: 16))
                            .foregroundColor(appPrimaryFontColor.opacity(0.5))
                    }
                    .frame(width: 28, height: 28)
                    .disabled(true)
                    .buttonStyle(.plain)
                    
                    // Send button
                    if viewModel.isLoading {
                        ProgressView()
                            .scaleEffect(0.8)
                            .frame(width: 44, height: 44)
                    } else {
                        Button(action: {
                            if !messageInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || !viewModel.draftAttachmentData.isEmpty {
                                viewModel.sendMessage(messageInput)
                                messageInput = ""
                            }
                        }) {
                            Image(systemName: "arrow.up.circle.fill")
                                .font(.system(size: 28))
                                .foregroundColor(
                                    (!messageInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || !viewModel.draftAttachmentData.isEmpty) 
                                    ? appPrimaryFontColor
                                    : appPrimaryFontColor.opacity(0.5)
                                )
                        }
                        .frame(width: 44, height: 44)
                        .buttonStyle(.plain)
                        .disabled(messageInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && viewModel.draftAttachmentData.isEmpty)
                    }
                }
                .padding(.horizontal, 12)
                .frame(height: 44)
            }
            .background(Color.white)
            .overlay(
                inputBarBorder
            )
            .padding(.horizontal, 0) // Remove horizontal padding to extend full width
            .padding(.top, 16) // Only add padding to the top
            .background(Color.white)
            .frame(maxWidth: .infinity) // Extend full width
        }
        .frame(maxWidth: .infinity)
        .animation(.spring(response: 0.3, dampingFraction: 0.8), value: viewModel.draftAttachmentData.isEmpty)
    }
    
    // MARK: - Input Bar Border
    private var inputBarBorder: some View {
        VStack(spacing: 0) {
            // Top shading/shadow effect
            Rectangle()
                .fill(
                    LinearGradient(
                        gradient: Gradient(colors: [
                            appPrimaryFontColor.opacity(0.1),
                            Color.clear
                        ]),
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .frame(height: 1)
            
            Spacer()
        }
    }
}

// MARK: - Attachment Preview Section
struct AttachmentPreviewSection: View {
    let attachmentData: [Data]
    let onRemove: (Int) -> Void
    let horizontalSizeClass: UserInterfaceSizeClass?
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(attachmentData.indices, id: \.self) { index in
                    ZStack(alignment: .topTrailing) {
                        if let uiImage = UIImage(data: attachmentData[index]) {
                            Image(uiImage: uiImage)
                                .resizable()
                                .scaledToFill()
                                .frame(width: 60, height: 60)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.gray.opacity(0.5), lineWidth: 1)
                                )
                        } else {
                            Rectangle()
                                .fill(appPrimaryFontColor.opacity(0.2))
                                .frame(width: 60, height: 60)
                                .cornerRadius(8)
                                .overlay(
                                    Image(systemName: "exclamationmark.triangle")
                                        .foregroundColor(.white)
                                )
                        }
                        
                        Button(action: { onRemove(index) }) {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundColor(appPrimaryFontColor.opacity(0.7))
                                .background(appBackgroundColor.opacity(0.7))
                                .clipShape(Circle())
                        }
                        .padding(4)
                        .buttonStyle(.plain)
                    }
                }
            }
            .padding(.horizontal, horizontalSizeClass == .regular ? 16 : 8)
            .padding(.top, 8)
        }
        .frame(height: 70)
        .transition(.opacity.combined(with: .scale(scale: 0.8, anchor: .bottom)))
    }
}
