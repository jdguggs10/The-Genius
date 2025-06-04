//
//  SettingsView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI

private let appBackgroundColor = Color(red: 253/255, green: 245/255, blue: 230/255) // FDF5E6
private let appPrimaryFontColor = Color(red: 61/255, green: 108/255, blue: 104/255) // 3D6C68

struct SettingsView: View {
    @Binding var isPresented: Bool // Added for controlling presentation in detail view
    let onDismiss: (() -> Void)? // Callback for custom dismiss behavior
    @Environment(\.dismiss) private var dismiss
    @State private var showingLoginView = false // State to present LoginView
    @State private var showingESPNLoginWebView = false // State to present ESPNLoginWebView
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @EnvironmentObject var appSettings: AppSettings
    @EnvironmentObject var conversationManager: ConversationManager
    
    // Default initializer for compatibility
    init(isPresented: Binding<Bool>, onDismiss: (() -> Void)? = nil) {
        self._isPresented = isPresented
        self.onDismiss = onDismiss
    }
    
    var body: some View {
        NavigationStack {
            List {
                Section {
                    profileSection
                } header: {
                    Text("Profile")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline) // Adaptive header font
                        .fontWeight(.semibold) // Bolder headers
                        .foregroundColor(.primary)
                }
                
                Section {
                    accountSection
                } header: {
                    Text("Account")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                }
                
                Section {
                    integrationsSection
                } header: {
                    Text("Integrations")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                }
                
                // Dark Mode Preference Section
                Section {
                    Picker("", selection: $appSettings.darkModeOption) {
                        ForEach(AppSettings.DarkModeOption.allCases) { option in
                            Text(option.displayName).tag(option)
                        }
                    }
                    .pickerStyle(.segmented)
                    .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)
                } header: {
                    Text("Dark Mode")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                }
                
                Section {
                    usageSection
                } header: {
                    Text("Usage")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                }
                
                Section {
                    aboutSection
                } header: {
                    Text("About The Genius")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                }
            }
            .listStyle(.insetGrouped) // Standard iOS settings style
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(horizontalSizeClass == .regular ? .large : .inline) // Large title on iPad
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Image("appstore")
                        .resizable()
                        .scaledToFit()
                        .frame(width: horizontalSizeClass == .regular ? 32 : 24,
                               height: horizontalSizeClass == .regular ? 32 : 24)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        onDismiss?() // Call the dismiss callback first
                        isPresented = false // Explicitly set to false for detail view dismissal
                        dismiss()
                    }
                    .font(.headline) // Make "Done" more prominent
                    .frame(minWidth: 44, minHeight: 44) // Ensure touch target
                    .foregroundColor(.primary)
                }
            }
            .sheet(isPresented: $showingESPNLoginWebView) {
                ESPNLoginWebView()
            }
        }
        // Apply a maximum width for the settings view on iPad if it's not meant to be full screen
        // This is often handled by how it's presented (e.g. .sheet or .popover)
        // .frame(maxWidth: horizontalSizeClass == .regular ? 600 : .infinity) // Example constraint
        .background(appBackgroundColor)
    }
    
    // MARK: - Profile Section
    private var profileSection: some View {
        HStack(spacing: horizontalSizeClass == .regular ? 20 : 16) { // More spacing on iPad
            Image("appstore")
                .resizable()
                .scaledToFit()
                .frame(width: horizontalSizeClass == .regular ? 80 : 66, height: horizontalSizeClass == .regular ? 80 : 66)
                .clipShape(Circle())
            
            VStack(alignment: .leading, spacing: horizontalSizeClass == .regular ? 6 : 4) {
                Text("John Doe")
                    .font(horizontalSizeClass == .regular ? .title : .headline) // Larger name on iPad
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
                
                Text("john.doe@example.com")
                    .font(horizontalSizeClass == .regular ? .headline : .subheadline) // Larger email on iPad
                    .foregroundColor(.secondary)
                
                Button("Login / Sign Up") { // Changed button text
                    showingLoginView = true   // Present LoginView
                }
                .font(horizontalSizeClass == .regular ? .body : .caption) // Larger button text on iPad
                .foregroundColor(appPrimaryFontColor) // Keep accent color for actions
                .padding(.top, horizontalSizeClass == .regular ? 4 : 2)
                .frame(minHeight: 44) // Ensure touch target
            }
            Spacer()
        }
        .padding(.vertical, horizontalSizeClass == .regular ? 12 : 8) // More vertical padding on iPad
    }
    
    // MARK: - Account Section
    private var accountSection: some View {
        Group {
            HStack {
                Label {
                    Text("Account Status").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "person.crop.circle.badge.checkmark").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                VStack(alignment: .trailing, spacing: 2) {
                    Text("Genius Pro").font(.subheadline).fontWeight(.semibold).foregroundColor(.orange)
                    Text("Premium").font(.caption).foregroundColor(.secondary)
                }
            }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4) // Adaptive padding

            HStack {
                Label {
                    Text("Manage Subscription").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "creditcard.and.arrow.up").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Manage subscription action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)
        }
        .font(horizontalSizeClass == .regular ? .headline : .body) // Base font for rows
    }
    
    // MARK: - Integrations Section
    private var integrationsSection: some View {
        Group {
            integrationRow(title: "ESPN Fantasy", subtitle: "Connected", icon: "football.fill", iconColor: appPrimaryFontColor, isConnected: true)
                .onTapGesture { // Modified onTapGesture
                    showingESPNLoginWebView = true
                }
            // integrationRow(title: "Yahoo Fantasy", subtitle: "Not Connected", icon: "y.circle.fill", iconColor: .purple, isConnected: false)
            // integrationRow(title: "Sleeper", subtitle: "Not Connected", icon: "moon.zzz.fill", iconColor: .indigo, isConnected: false)
            
            HStack {
                Label {
                    Text("Add Integration").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "plus.app.fill").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { 
                showingESPNLoginWebView = true
            }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)
        }
        .font(horizontalSizeClass == .regular ? .headline : .body)
    }
    
    private func integrationRow(title: String, subtitle: String, icon: String, iconColor: Color, isConnected: Bool) -> some View {
        HStack(spacing: horizontalSizeClass == .regular ? 16 : 12) {
            Image(systemName: icon)
                .foregroundColor(iconColor)
                .font(horizontalSizeClass == .regular ? .title2 : .title3) // Larger icons on iPad
                .frame(width: 30, alignment: .center) // Ensure icons are aligned
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title).foregroundColor(.primary) // Update text color
                Text(subtitle)
                    .font(horizontalSizeClass == .regular ? .subheadline : .caption)
                    .foregroundColor(isConnected ? .green : .secondary)
            }
            Spacer()
            if isConnected {
                Image(systemName: "checkmark.circle.fill").foregroundColor(.green)
                    .font(horizontalSizeClass == .regular ? .title3 : .body)
            } else {
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
        }
        .padding(.vertical, horizontalSizeClass == .regular ? 8 : 6) // Adaptive padding
        .contentShape(Rectangle())
        .onTapGesture { /* Integration management action */ }
    }
    
    // MARK: - Usage Section
    private var usageSection: some View {
        Group {
            HStack {
                Label {
                    Text("Monthly Usage").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "chart.bar.xaxis").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                VStack(alignment: .trailing, spacing: 2) {
                    Text("847 / 1000").font(.subheadline).fontWeight(.medium)
                    Text("Queries Used").font(.caption).foregroundColor(.secondary)
                }
            }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label {
                    Text("Usage History").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "clock.arrow.circlepath").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Usage history action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label {
                    Text("Reset Usage").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "arrow.counterclockwise.circle.fill").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Reset usage action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)
        }
        .font(horizontalSizeClass == .regular ? .headline : .body)
    }
    
    // MARK: - About Section
    private var aboutSection: some View {
        Group {
            HStack {
                Label {
                    Text("Version").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "app.badge.checkmark.fill").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                Text("1.0.0 (Build 1)").font(.subheadline).foregroundColor(.secondary)
            }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label {
                    Text("What's New").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "star.bubble.fill").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* What's new action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label {
                    Text("Help & Support").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "lifepreserver.fill").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Help & support action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label {
                    Text("Privacy Policy").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "lock.doc.fill").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Privacy policy action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label {
                    Text("Terms of Service").foregroundColor(.primary)
                } icon: {
                    Image(systemName: "doc.plaintext.fill").foregroundColor(appPrimaryFontColor)
                }
                
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Terms of service action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)
        }
        .font(horizontalSizeClass == .regular ? .headline : .body)
    }
}
