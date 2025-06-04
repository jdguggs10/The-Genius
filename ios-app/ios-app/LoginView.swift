import SwiftUI

private let appBackgroundColor = Color(red: 253/255, green: 245/255, blue: 230/255) // FDF5E6
private let appPrimaryFontColor = Color(red: 61/255, green: 108/255, blue: 104/255) // 3D6C68

struct LoginView: View {
    @Environment(\.dismiss) var dismiss
    @State private var email = ""
    @State private var password = ""
    @State private var showingPasswordReset = false // Optional
    @State private var showingSignUp = false // Optional
    @EnvironmentObject var appSettings: AppSettings
    @State private var apiKey: String = ""
    @State private var showingProgress = false
    @State private var showErrorAlert = false;
    @State private var errorMessage: String = ""

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Spacer()
                
                Image(systemName: "key.shield.fill") // Using an SF Symbol
                    .resizable()
                    .scaledToFit()
                    .frame(width: 80, height: 80)
                    .foregroundColor(appPrimaryFontColor)
                
                Text("Enter API Key")
                    .font(.title2)
                    .fontWeight(.semibold)
                    .foregroundColor(appPrimaryFontColor)
                
                SecureField("API Key", text: $apiKey)
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color.white) // Keep text field white for contrast
                            .stroke(appPrimaryFontColor.opacity(0.5), lineWidth: 1)
                    )
                    .foregroundColor(appPrimaryFontColor)
                    .textContentType(.oneTimeCode) // Helps with password managers if applicable
                    .submitLabel(.done)
                    .padding(.horizontal)
                
                if showingProgress {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: appPrimaryFontColor))
                        .scaleEffect(1.5)
                } else {
                    Button(action: login) {
                        Text("Continue")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .foregroundColor(.white)
                            .background(appPrimaryFontColor)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal)
                }
                
                Spacer()
                Spacer()
            }
            .padding()
            .background(appBackgroundColor.edgesIgnoringSafeArea(.all))
            .alert("Login Error", isPresented: $showErrorAlert, actions: {
                Button("OK", role: .cancel) { }
            }, message: {
                Text(errorMessage)
            })
            .onAppear {
                // Pre-fill with stored key if available, useful for returning users
                apiKey = appSettings.apiKey
            }
            .navigationTitle("Login")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    private func login() {
        guard !apiKey.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            errorMessage = "API Key cannot be empty."
            showErrorAlert = true
            return
        }
        
        // Basic validation (e.g. length or prefix if known)
        // This is just an example, update with actual validation logic
        if apiKey.count < 10 { // Example: API keys are usually longer
            errorMessage = "Invalid API Key format."
            showErrorAlert = true
            return
        }
        
        showingProgress = true
        // Simulate network request or validation
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            // On successful validation:
            appSettings.apiKey = apiKey
            appSettings.isLoggedIn = true
            showingProgress = false
            
            // If login fails (example):
            // self.errorMessage = "The API Key provided is invalid."
            // self.showErrorAlert = true
            // self.showingProgress = false
        }
    }
}

#Preview {
    LoginView()
        .environmentObject(AppSettings())
}
