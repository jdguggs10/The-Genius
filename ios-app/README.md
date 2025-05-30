# Fantasy Genius - iOS App

This is the native iOS companion app for the Fantasy Genius AI assistant. It provides a user-friendly chat interface to interact with the AI, get fantasy sports advice, and view structured responses.

## ✨ Features

- **Chat Interface**: Send messages to and receive responses from the Fantasy Genius AI.
- **Streaming Responses**: Receives advice from the backend as a stream of JSON chunks, which are then parsed and displayed.
- **Structured Advice Display**: Assistant responses are parsed from a defined JSON structure (`StructuredAdviceResponse`) and displayed with details such as:
    - Main Advice
    - Reasoning
    - Confidence Score
    - Alternative Options
    - AI Model Used
- **Conversation History**: Saves and loads your chat history locally on the device.
- **Attachment Support (Basic)**: Allows attaching images to messages (further backend integration for processing attachments would be needed).
- **Error Handling**: Displays errors from network requests or data parsing.

## 🔧 Technology Stack

- **SwiftUI**: For building the user interface.
- **Combine & async/await**: For handling asynchronous operations and network requests.
- **URLSession**: For making HTTP requests to the backend API.
- **Codable**: For encoding and decoding JSON data (requests and responses).

## 🔌 Backend Connection

- The app connects to the Fantasy AI Backend to send user queries and receive AI-generated advice.
- **Default Backend URL**: `https://genius-backend-nhl3.onrender.com/advice` (configurable in `ChatViewModel.swift`).
- **API Interaction**:
    - Sends POST requests to the `/advice` endpoint.
    - The request body is a JSON payload (`AdviceRequestPayload`) containing the conversation history.
    - The response is a stream of JSON chunks (`application/x-ndjson`) which, when assembled, form a `StructuredAdviceResponse` object.

## 📂 Project Structure (Key Files in `ios-app/ios-app/`)

- **`ios_appApp.swift`**: The main entry point of the SwiftUI application.
- **`ContentView.swift`**: Defines the main UI, including the chat list and input bar.
- **`ChatViewModel.swift`**: The MVVM ViewModel that manages chat logic, state, and communication with the backend API. This is where network requests for streaming advice are handled.
- **`Message.swift`**: Defines the `Message` struct used for displaying chat messages. It now includes an optional `structuredAdvice` field to hold the parsed JSON response from the assistant.
- **`NetworkModels.swift`**: Contains Swift `Codable` structs that map to the JSON payloads for API requests (`AdviceRequestPayload`, `MessagePayload`) and responses (`StructuredAdviceResponse`, `AdviceAlternativePayload`).
- **`MessageBubble.swift`**: A SwiftUI view responsible for rendering individual chat messages, including the detailed structured advice from the assistant.

## 🚀 Getting Started

1.  **Ensure Backend is Running**: Make sure the [Fantasy AI Backend](https://github.com/your-repo/the-genius/tree/main/backend) (replace with your actual repo link if different) is running and accessible. By default, the app points to `https://genius-backend-nhl3.onrender.com/advice`.
    *   If testing with a local backend, update `backendURLString` in `ChatViewModel.swift` to `http://localhost:8000/advice` (or your local IP if testing on a physical device).
2.  **Open in Xcode**: Open the `ios-app/ios-app.xcodeproj` file in Xcode.
3.  **Select a Simulator or Device**: Choose an appropriate target (e.g., iPhone simulator or a connected physical device).
4.  **Build and Run**: Click the "Play" button (or Cmd+R) in Xcode to build and run the application.

## 🛠️ How It Works (Streaming & Structured JSON)

1.  When a user sends a message, `ChatViewModel` constructs an `AdviceRequestPayload`.
2.  It makes a POST request to the backend `/advice` endpoint using `URLSession`.
3.  The backend streams JSON data (as text chunks) representing a `StructuredAdviceResponse` object.
4.  `ChatViewModel` accumulates these chunks using `URLSession.shared.bytes(for: request)`.
5.  Once the stream is complete, the accumulated data is decoded from a JSON string into a `StructuredAdviceResponse` Swift object.
6.  The `mainAdvice` from this object updates the content of the assistant's message bubble, and the full `structuredAdvice` object is stored within the `Message` struct.
7.  `MessageBubble.swift` then displays the `mainAdvice` along with other details like reasoning, confidence, and alternatives if present.

## 📝 Future Considerations & Improvements

- **Enhanced Attachment Handling**: Currently, images can be attached, but the backend doesn't process them. This could be extended (e.g., for image analysis related to fantasy sports).
- **User Authentication**: Implement user accounts if needed.
- **Settings Screen**: Add options for user preferences (e.g., default model, display options).
- **UI/UX Refinements**: Further polish the chat interface, animations, and overall user experience.
- **More Robust Error Display**: Provide more contextual error messages or retry mechanisms.

---
This README provides an overview of the Fantasy Genius iOS app. For backend details, refer to the backend's README file.

## 🤖 AI Reviewer Notes

For AI agents reviewing this iOS application, the following points are crucial for understanding its architecture and core logic:

-   **`ChatViewModel.swift`**: This class is central to the app's functionality and follows the MVVM (Model-View-ViewModel) pattern. It handles:
    -   Managing the state of the chat (e.g., conversation history, loading indicators).
    -   Orchestrating network requests to the backend for streaming AI advice.
    -   Processing incoming streamed data, including accumulating chunks and decoding the final JSON payload.
    -   Updating the UI through published properties that SwiftUI views observe.
    -   Error handling for network operations and data parsing.
-   **`ContentView.swift`**: This is the main SwiftUI view that structures the user interface. It observes `ChatViewModel` for data and state changes to render the chat messages, input fields, and other UI elements.
-   **`NetworkModels.swift`**: This file contains the Swift `Codable` structs (e.g., `AdviceRequestPayload`, `StructuredAdviceResponse`, `MessagePayload`, `AdviceAlternativePayload`) that define the exact structure for data exchanged with the backend API. These models are critical for successful serialization and deserialization of JSON.
-   **`Message.swift` and `MessageBubble.swift`**:
    -   `Message.swift`: Defines the data structure for individual chat messages, including storing the text, user information, and the parsed `StructuredAdviceResponse`.
    -   `MessageBubble.swift`: A SwiftUI view responsible for the visual representation of each message in the chat interface, including the display of structured advice details.
-   **Streaming Mechanism**: The app uses `URLSession.shared.bytes(for: request)` to handle the streaming response from the backend. This approach allows for efficient processing of data as it arrives, rather than waiting for the entire response. Look for this in `ChatViewModel.swift`.
-   **Error Handling**: Primary error handling logic related to network requests and data processing is implemented within `ChatViewModel.swift`. This includes updating the UI to inform the user of any issues.
-   **Backend URL Configuration**: The backend URL is a configurable variable (e.g., `backendURLString`) within `ChatViewModel.swift`, with a default value pointing to the production deployment.