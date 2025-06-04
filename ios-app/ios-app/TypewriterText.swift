import SwiftUI

struct TypewriterText: View {
    let text: String
    var typingSpeed: Double = 0.03 // seconds per character
    @State private var displayedText: String = ""
    @State private var currentIndex: Int = 0
    @State private var typingTask: Task<Void, Never>? = nil

    var body: some View {
        Text(displayedText)
            .onAppear { startTyping(for: text) }
            .onChange(of: text) { newValue in
                startTyping(for: newValue)
            }
    }

    private func startTyping(for newText: String) {
        typingTask?.cancel()
        if newText.count < currentIndex {
            displayedText = ""
            currentIndex = 0
        }
        typingTask = Task {
            let characters = Array(newText)
            while currentIndex < characters.count {
                let char = characters[currentIndex]
                await MainActor.run { displayedText.append(char) }
                currentIndex += 1
                try? await Task.sleep(nanoseconds: UInt64(typingSpeed * 1_000_000_000))
            }
        }
    }
}
