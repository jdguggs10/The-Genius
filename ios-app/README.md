# iOS Fantasy Genius App

## Overview

The iOS Fantasy Genius app is a SwiftUI-based mobile client designed to provide AI-powered fantasy sports advice through real-time streaming conversations. The app leverages a robust backend (OpenAI's GPT-4.1-Mini Responses API via a FastAPI backend) to deliver contextual and structured fantasy sports recommendations. It features a responsive user interface that adapts to different screen sizes and orientations, ensuring a seamless experience on both iPhone and iPad.

## Key Features

- **📱 Adaptive UI**: Responsive design that adjusts layout for compact and regular horizontal size classes (iPhone/iPad).
- **🗨️ Real-time Chat Interface**: Streaming conversations with Fantasy Genius AI, showing live typing effects and status updates.
- **💬 Conversation Management**: Persistent chat history, ability to start new conversations, and clear context.
- **🖼️ Image Attachments**: Users can attach images to messages, with previews in the input bar.
- **👉 Swipe Gestures**: Intuitive swipe gestures for common actions like initiating a new conversation.
- **⚙️ Settings Management**: In-app settings accessible via a modal sheet (compact) or a detail view (regular).
- **📊 Structured Advice**: Detailed responses with reasoning, confidence scores, and alternatives.
- **🔍 Web Search Integration**: Real-time sports data via built-in search tools (facilitated by backend).
- **🔒 ESPN Integration**: Allows users to log into their ESPN accounts via an in-app WebView. Session cookies (`espn_s2` and `SWID`) are securely extracted and stored.

## Application Architecture

The application is built using SwiftUI and follows the MVVM (Model-View-ViewModel) design pattern.

### UI Structure
- **`ContentView.swift`**: The main entry point for the UI. It manages the overall layout and adapts based on the horizontal size class.
    - **Compact Layout (e.g., iPhone Portrait)**: Uses a `ZStack` to manage a slide-out `SidebarView` and a main `NavigationStack` for chat content or settings.
    - **Regular Layout (e.g., iPad)**: Employs a `NavigationSplitView` with `SidebarView` in the primary column and the chat content or `SettingsView` in the detail column.
- **`SidebarView.swift`**: Displays a list of conversations and provides access to app settings.
- **`ChatViewModel.swift`**: Manages the state and logic for a single conversation, including message fetching, sending, SSE handling, and image attachments.
- **`ConversationManager.swift`**: Handles the creation, storage, and retrieval of multiple conversations.
- **Message Display**:
    - **`MessageListView`**: A scrollable view displaying `MessageBubble` instances for each message.
    - **`MessageBubble.swift`**: Renders individual chat messages, distinguishing between user and AI.
- **Input Handling**:
    - **`InputBarView` (within `ContentView.swift`) / `InputBar.swift` (refactored component)**: A dedicated component for text input, image selection (via `PhotosPicker`), and sending messages. Includes attachment previews.
- **Settings**:
    - **`SettingsView.swift`**: Provides UI for application settings, presented modally or in the detail view.
- **State Management**:
    - Primarily uses SwiftUI's built-in property wrappers: `@State`, `@StateObject`, `@ObservedObject`, `@EnvironmentObject`, and `@Environment`.
    - `ConversationManager` and `ChatViewModel` are key observable objects driving the UI.
- **Navigation**:
    - `NavigationStack` is used for drill-down navigation within the chat detail and settings.
    - `NavigationSplitView` manages the master-detail interface in regular layouts.
    - Programmatic navigation is used for selecting conversations and presenting settings.

### Core SwiftUI Components Utilized
- `GeometryReader`: For dynamic layout adjustments based on available space.
- `ScrollViewReader`: To automatically scroll to the latest message in the chat.
- `LazyVStack`: For efficient rendering of message lists.
- `PhotosPicker`: For selecting images from the user's photo library.
- `NavigationSplitViewVisibility`: To control the visibility of columns in `NavigationSplitView`.
- `.task` and `async/await`: For performing asynchronous operations like fetching data and processing images.
- `.onChange`: To react to state changes and trigger updates (e.g., layout changes on size class change, loading conversation on selection).

## 🚨 Recent SSE Issues Resolution

This app has been **significantly improved** to resolve SSE (Server-Sent Events) issues and implement proper OpenAI Responses API integration patterns.

### ✅ **Issues Resolved**

| Issue | Problem | Solution |
|-------|---------|----------|
| **Context Loss** | App wasn't maintaining conversation context between turns | Implemented `previous_response_id` tracking for server-side state management |
| **Inefficient API Usage** | Sending full conversation history with each request | Smart request logic: uses `previous_response_id` when available, falls back to full history for new conversations |
| **Limited SSE Support** | Only basic event types supported | Enhanced support for all official Responses API events (`response.output_text.delta`, `response.web_search_call.searching`, etc.) |
| **No Context Management** | No way to reset or manage conversation state | Added `startNewConversation()` and `resetConversationContext()` methods with UI controls |

### 🔧 **Key Technical Improvements**

#### Enhanced Network Models
```swift
// From NetworkModels.swift (example, ensure this matches actual file)
struct AdviceRequestPayload: Codable {
    let previousResponseId: String? // Responses API state management
    let userMessage: String
    let model: String?
    let enableWebSearch: Bool?
    // ... other relevant fields ...

    // Convenience initializer for continuing conversations
    init(userMessage: String, previousResponseId: String, model: String? = nil, enableWebSearch: Bool? = nil) {
        self.userMessage = userMessage
        self.previousResponseId = previousResponseId
        self.model = model
        self.enableWebSearch = enableWebSearch
        // ...
    }
}

// From Conversation.swift (example, ensure this matches actual file)
struct Conversation: Identifiable, Codable, Equatable {
    var id: UUID
    var title: String
    var messages: [Message]
    var lastResponseId: String? // Track OpenAI response ID

    mutating func updateLastResponseId(_ responseId: String?) {
        self.lastResponseId = responseId
    }
    mutating func resetConversationState() {
        self.lastResponseId = nil
        // Potentially clear messages or other state if needed by app logic
    }
}
```

#### Smart Request Logic
- **Continuing Conversations**: Uses `previous_response_id` + new message only (optimal).
- **New Conversations**: Sends full conversation history as fallback.
- **Dynamic Model Selection**: Fetches current backend default model or uses `gpt-4.1-mini` fallback.
- **Response ID Tracking**: Captures and stores IDs from SSE events.

#### Model Configuration Management
```swift
// Example from ApiConfiguration.swift or similar
// Dynamic model fetching from backend
func fetchBackendDefaultModel() async -> String? { /* ... */ }
private func getModelToUse() async -> String { /* ... */ }

// Automatic sync with backend's current default model
// Falls back to gpt-4.1-mini if backend is unavailable
```

#### Enhanced SSE Event Handling
```swift
// ChatViewModel.swift now supports official Responses API events:
// - "response.output_text.delta"        // Official text streaming
// - "response.web_search_call.searching"// Web search status
// - "response.completed"                // Official completion
// - "response_created"                  // Response ID capture (or similar custom event for ID)
// - "status_update"                     // Backend custom events for status messages
```

### 🎯 **Responses API Best Practices Implemented**

1. ✅ **Dynamic model selection** synced with backend configuration.
2. ✅ **Server-side state management** with `previous_response_id`.
3. ✅ **Optimized token usage** - only new messages sent when continuing.
4. ✅ **Official event handling** for all Responses API event types.
5. ✅ **Built-in tools support** for web search integration.

### 🧪 **Testing Multi-Turn Context**

Test these scenarios to verify improvements:
```
1. Context Continuity:
   → "Who is Patrick Mahomes?"
   → "What are his stats this season?" (should understand "his" = Mahomes)

2. Context Reset (if applicable via UI):
   → Use toolbar menu → "Reset Context" or similar action
   → Follow-up questions start fresh without prior context

3. New Conversation:
   → Use toolbar menu → "New Conversation"
   → Proper state initialization and context separation
```

### 🏗️ **Architecture Benefits (from API improvements)**

- **Reduced Token Usage**: Significant reduction using `previous_response_id`.
- **Better Performance**: Faster responses via server-side state management.
- **Enhanced Reliability**: Proper error handling and fallback mechanisms.
- **Future-Proof**: Aligned with OpenAI's latest API patterns.
- **Improved UX**: Contextually aware multi-turn conversations.

---

## 🔧 Technology Stack

- **SwiftUI**: Modern declarative UI framework for iOS.
- **Combine & async/await**: For asynchronous operations and reactive programming.
- **URLSession**: For HTTP streaming and handling Server-Sent Events (SSE).
- **Codable**: For type-safe JSON encoding and decoding.
- **PhotosUI**: For accessing the photo library (specifically `PhotosPicker`).
- **WebKit**: For in-app web browsing (used for ESPN Login via `WKWebView`).
- **OpenAI Responses API**: GPT-4.1-Mini (or backend-configured model) with built-in tools integration.

## 🚀 Getting Started

1.  **Prerequisites**: iOS 16.0+ (Verify specific version if changed), Xcode 15.0+ (Verify specific version).
2.  **Backend Setup**: Ensure the Fantasy AI Backend is running.
    *   **Production**: Typically `https://genius-backend-nhl3.onrender.com/advice`.
    *   **Local Development**: Ensure your local backend is running (e.g., at `http://localhost:8000`).
3.  **Build & Run**: Open `ios-app.xcodeproj` in Xcode and run on a simulator or physical device.

### Local Development Configuration
To test against a local backend (e.g., `http://localhost:8000`):

1.  Open the file `ios-app/ios-app/ApiConfiguration.swift`.
2.  Locate the `getBackendBaseURL()` function.
3.  Inside the `#if DEBUG` block, ensure `return localBackendURL` is uncommented and `return productionBackendURL` is commented out:

    ```swift
    #if DEBUG
    // In debug mode, use the local backend
    return localBackendURL // Ensure this line is uncommented
    // return productionBackendURL // Ensure this line is commented out
    #else
    // In release mode, use the production backend
    return productionBackendURL
    #endif
    ```
The app will then use `http://localhost:8000` for its API requests when built in the `Debug` configuration.

## 📂 Key Files & Structure

| File/Directory         | Purpose                                                                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `ios-app/`             | Main application module.                                                                                                              |
| ├── `ContentView.swift`  | Root view managing overall UI layout (adapts to compact/regular size classes), navigation, and gesture handling. Also handles input bar functionality. |
| ├── `ChatViewModel.swift`| MVVM ViewModel for chat logic, API interaction, SSE handling, image processing, and state for a single conversation.                |
| ├── `Conversation.swift` | Data model for a single conversation, including messages and `lastResponseId`.                                                        |
| ├── `Models.swift`       | Contains core data models for the application, such as `Message`.                                                                     |
| ├── `NetworkModels.swift`| Defines `Codable` structures for API requests (e.g., `AdviceRequestPayload`) and responses.                                       |
| ├── `ApiConfiguration.swift`| Manages backend API endpoint URLs (local/production) and model configuration.                                                      |
| ├── `SidebarView.swift`  | UI for displaying conversation list and accessing settings; part of `NavigationSplitView` or slide-out panel. Works with `ContentView` and `ChatViewModel` for conversation management. |
| ├── `SettingsView.swift` | UI for application settings.                                                                                                          |
| ├── `MessageRow.swift`   | View for displaying a single row in the chat, containing either a user or assistant message.                                        |
| ├── `AssistantBubble.swift`| View for rendering AI/assistant messages with specific styling.                                                                     |
| ├── `UserBubble.swift`   | View for rendering user messages with specific styling.                                                                               |
| ├── `BubbleShell.swift`  | A container view or modifier for chat bubbles, providing common styling or layout.                                                  |
| ├── `MessageBubble.swift`| Generic view for rendering individual chat messages, potentially used by or in conjunction with `AssistantBubble` and `UserBubble`. |
| ├── `DetailsCardView.swift`| A reusable card view component for displaying detailed information.                                                                 |
| ├── `Constants.swift`    | Defines global constants used throughout the application.                                                                            |
| ├── `AppSettings.swift`  | Manages application-level settings and their persistence.                                                                           |
| ├── `LoginView.swift`    | Provides a UI for user authentication.                                                                                                |
| ├── `ios_appApp.swift`   | The main entry point of the application, conforming to the `App` protocol.                                                            |
| ├── `PhotosPicker`       | (SwiftUI Component) Utilized for image selection from the user's photo library.                                                      |
| ├── `WebView.swift`      | Generic SwiftUI wrapper for `WKWebView`.                                                                                              |
| ├── `ESPNLoginWebView.swift` | Specific `WebView` implementation for the ESPN login flow.                                                                         |
| ├── `ESPNCookieManager.swift` | Manages ESPN session cookies (storage and retrieval using `UserDefaults`).                                                        |
| ├── `ios-app.entitlements` | Project configuration file defining application capabilities and permissions.                                                       |
| `Assets.xcassets/`     | App icons, custom colors (e.g., `appBackgroundColor`, `appPrimaryFontColor`).                                                         |
| `ios-app.xcodeproj/`   | Xcode project file.                                                                                                                   |

## 🔌 API Integration

- **Endpoint**: `POST /advice` (or as configured in `ApiConfiguration.swift`) with an SSE streaming response.
- **Authentication**: The backend service handles OpenAI API key management.
- **Request Format**: `AdviceRequestPayload` (defined in `NetworkModels.swift`), which includes the user's message, and optionally `previousResponseId` for context continuity, along with other parameters like model choice or web search enablement.
- **Response Format**: Server-Sent Events (SSE) stream, with events like `response.output_text.delta`, `response.web_search_call.searching`, `response.completed`, and custom events like `response_created` or `status_update`. These are parsed into structured data, often culminating in a `StructuredAdviceResponse` or similar model.

### SSE Event Flow Example
```
1. User types message and taps send (or attaches image).
2. `ChatViewModel` prepares `AdviceRequestPayload`.
   - If `conversation.lastResponseId` exists, it's included.
   - Otherwise, full (or relevant part of) message history might be sent (though `previous_responseId` is preferred).
3. Request is sent to the backend API.
4. Backend streams SSE events:
   - `response_created` (or similar custom event): provides the `responseId` for the current turn.
   - `status_update`: provides intermediate status messages (e.g., "Searching web...").
   - `response.output_text.delta`: streams parts of the AI's text response.
   - `response.web_search_call.searching` / `response.web_search_call.results`: if web search is used.
   - `response.completed`: signals the end of the AI's response for this turn.
5. `ChatViewModel` processes these events in real-time:
   - Updates `viewModel.messages` with new text.
   - Displays status messages.
   - Stores the `responseId` in `conversation.lastResponseId` upon completion or receipt.
6. UI (e.g., `MessageListView`, `MessageBubble`) updates reactively to show new content and statuses.
```

## ESPN Integration Details

The ESPN integration allows users to log into their ESPN accounts. This is a foundational step for potential future features that might leverage personalized fantasy sports data.

### Login Flow
1.  **Initiation**: The user navigates to "Settings" (via `SidebarView`) and selects an "ESPN Fantasy" (or similar) integration option.
2.  **WebView Presentation**: `ESPNLoginWebView.swift` (which uses the generic `WebView.swift`) is presented, typically as a sheet.
3.  **Authentication URL**: The `WKWebView` loads the ESPN login page (e.g., `https://secure.web.plus.espn.com/identity/login?...`).
4.  **User Authentication**: The user enters their ESPN credentials directly into the ESPN web page. The app itself does not handle or store these credentials.
5.  **Redirection & Cookie Extraction**: Upon successful login, ESPN redirects the WebView (e.g., to `https://www.espn.com/`). The `WKNavigationDelegate` (the nested `Coordinator` class within `WebView.swift`) detects navigation completion for relevant domains.
6.  **Cookie Retrieval**: The `Coordinator` accesses `WKWebsiteDataStore.default().httpCookieStore` to retrieve all HTTP cookies for the `espn.com` domain.
7.  **Cookie Storage**: The `onCookiesAvailable` callback in `ESPNLoginWebView.swift` filters these cookies for `espn_s2` and `SWID`. If found, these are passed to `ESPNCookieManager.shared.saveCookies()`, which currently stores them in `UserDefaults`.
8.  **Dismissal**: After cookie processing, the `ESPNLoginWebView` is typically dismissed automatically.

### Using Stored Cookies
To make authenticated requests to ESPN APIs (for future features):
```swift
if let cookieHeader = ESPNCookieManager.shared.getCookieHeader() {
    // Add this string to the "Cookie" HTTP header for your URLRequest
    // e.g., request.setValue(cookieHeader, forHTTPHeaderField: "Cookie")
}
```

### Security Note
Currently, ESPN session cookies (`espn_s2` and `SWID`) are stored in `UserDefaults`. While convenient for development, `UserDefaults` is **not secure** for sensitive session information. **For production, these cookies must be migrated to Keychain storage for enhanced security.**

## 🛠️ Development Notes & Best Practices

### Testing Context Management & UI Flow
-   Verify that `previous_response_id` is correctly used when continuing conversations.
-   Test the "New Conversation" functionality (toolbar button, swipe gesture) to ensure proper state reset and UI updates.
-   Test settings presentation and dismissal in both compact and regular layouts.
-   Validate image attachment flow: picking, previewing, sending, and (if applicable) displaying in chat.
-   Check error handling for API issues and image loading failures.

### Debugging
-   Use Xcode's console for logging SSE events, `responseId` tracking, and other debug information from `ChatViewModel` and `ConversationManager`.
-   Leverage SwiftUI Previews for isolated component testing.
-   Inspect `UserDefaults` (or Keychain, once implemented) to verify cookie storage if needed.

### Code Style and Structure
- Adhere to SwiftUI best practices (e.g., view composition, state management principles).
- Keep ViewModels focused on presentation logic and data transformation.
- Ensure services like `ConversationManager` and `ESPNCookieManager` have clear responsibilities.

## 📈 Performance
- **Image Processing**: Images selected via `PhotosPicker` are processed asynchronously in `ContentView.swift` (`processImageData`):
    - Resized to a maximum dimension (e.g., 1024px) to prevent excessive memory usage.
    - Compressed (e.g., JPEG with 0.8 quality).
    - Performance metrics (duration) for image processing are logged if exceeding a threshold.
- **Lazy Loading**: `LazyVStack` is used in `messageListView` for efficient scrolling through messages.
- **API Efficiency**: Use of `previous_response_id` significantly reduces token usage and improves response times for continued conversations.
- **Memory Management**: `autoreleasepool` is used during image processing to manage memory for `UIImage` objects.

---

## 🤖 AI Integration Details (For AI Agents/Code Review)

- **Core Logic**: `ChatViewModel.swift` is central to the AI interaction, managing the MVVM pattern, handling Responses API integration, SSE parsing, and state for individual conversations.
- **State Management (Context)**: The system primarily uses `previous_response_id` (stored in `Conversation.lastResponseId`) for maintaining conversational context with the backend. This is crucial for efficient and contextually accurate AI responses.
- **SSE Processing**: Robust line-by-line parsing of SSE events is implemented in `ChatViewModel.swift`, handling various event types including text deltas, status updates, completion signals, and response ID capture.
- **Error Recovery**: The app includes mechanisms for displaying errors from the API and attempts graceful fallbacks where possible.
- **Model Usage**: The app is designed to dynamically use the model specified by the backend configuration (via `ApiConfiguration.swift`), with a fallback to a default like `gpt-4.1-mini` if the backend config is unavailable. This aligns with OpenAI best practices.
- **Data Models**: Type-safe `Codable` structs (e.g., `AdviceRequestPayload`, `StructuredAdviceResponse` (from `NetworkModels.swift`), `Message` (from `Models.swift`), `Conversation`) are used for API communication and local data persistence, ensuring consistency with backend contracts.

The implementation is aligned with OpenAI's official Responses API patterns and has resolved previously noted SSE issues, aiming for a production-ready delivery of fantasy sports advice.