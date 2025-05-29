import SwiftUI

struct LoginView: View {
    @Environment(\.dismiss) var dismiss
    @State private var email = ""
    @State private var password = ""
    @State private var showingPasswordReset = false // Optional
    @State private var showingSignUp = false // Optional

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Spacer()
                Text("Welcome Back")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                TextField("Email", text: $email)
                    .keyboardType(.emailAddress)
                    .textContentType(.emailAddress)
                    .autocapitalization(.none)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)

                SecureField("Password", text: $password)
                    .textContentType(.password)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)

                Button(action: {
                    // TODO: Handle login logic
                    print("Login tapped with email: \(email)")
                    // For now, just dismiss
                    dismiss()
                }) {
                    Text("Login")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .cornerRadius(10)
                }

                // Optional: Forgot Password and Sign Up
                HStack {
                    Button("Forgot Password?") {
                        // showingPasswordReset = true // Action for password reset
                    }
                    .font(.caption)
                    Spacer()
                    Button("Sign Up") {
                        // showingSignUp = true // Action for sign up
                    }
                    .font(.caption)
                }
                
                Spacer()
                Spacer()
            }
            .padding(.horizontal, 30)
            .navigationTitle("Login")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            // Optional: Sheets for password reset or sign up
            // .sheet(isPresented: $showingPasswordReset) { Text("Password Reset View") }
            // .sheet(isPresented: $showingSignUp) { Text("Sign Up View") }
        }
    }
}

#Preview {
    LoginView()
}
