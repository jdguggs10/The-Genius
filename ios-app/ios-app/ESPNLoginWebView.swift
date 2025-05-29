import SwiftUI

struct ESPNLoginWebView: View {
    @Environment(\.dismiss) var dismiss
    // The prompt had a typo "https_" which is removed here.
    // private let espnURL = URL(string: "https://www.espn.com")! // Not directly used, URL is created inline

    var body: some View {
        NavigationStack {
            // Ensure URL is valid, directly used in WebView
            if let validURL = URL(string: "https://www.espn.com") { 
                WebView(url: validURL)
                    .navigationTitle("ESPN Login")
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .navigationBarLeading) {
                            Button("Done") {
                                dismiss()
                            }
                        }
                    }
            } else {
                Text("Error: Invalid URL") // Fallback for invalid URL
                    .navigationTitle("Error")
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .navigationBarLeading) {
                            Button("Done") {
                                dismiss()
                            }
                        }
                    }
            }
        }
    }
}

#Preview {
    ESPNLoginWebView()
}
