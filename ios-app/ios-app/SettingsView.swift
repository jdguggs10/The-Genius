//
//  SettingsView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI

struct SettingsView: View {
    @Binding var isPresented: Bool // Added for controlling presentation in detail view
    @Environment(\.dismiss) private var dismiss
    @State private var showingLoginView = false // State to present LoginView
    @State private var showingESPNLoginWebView = false // State to present ESPNLoginWebView
    @State private var isNotificationsEnabled = true
    @State private var isDarkModeEnabled = false
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    
    var body: some View {
        NavigationStack {
            List {
                Section {
                    profileSection
                } header: {
                    Text("Profile")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline) // Adaptive header font
                        .fontWeight(.semibold) // Bolder headers
                }
                
                Section {
                    accountSection
                } header: {
                    Text("Account")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                }
                
                Section {
                    integrationsSection
                } header: {
                    Text("Integrations")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                }
                
                Section {
                    usageSection
                } header: {
                    Text("Usage")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                }
                
                Section {
                    preferencesSection
                } header: {
                    Text("Preferences")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                }
                
                Section {
                    aboutSection
                } header: {
                    Text("About The Genius")
                        .font(horizontalSizeClass == .regular ? .title2 : .headline)
                        .fontWeight(.semibold)
                }
            }
            .listStyle(.insetGrouped) // Standard iOS settings style
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(horizontalSizeClass == .regular ? .large : .inline) // Large title on iPad
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        isPresented = false // Explicitly set to false for detail view dismissal
                        dismiss()
                    }
                    .font(.headline) // Make "Done" more prominent
                    .frame(minWidth: 44, minHeight: 44) // Ensure touch target
                }
            }
        }
        // Apply a maximum width for the settings view on iPad if it's not meant to be full screen
        // This is often handled by how it's presented (e.g. .sheet or .popover)
        // .frame(maxWidth: horizontalSizeClass == .regular ? 600 : .infinity) // Example constraint
    }
    
    // MARK: - Profile Section
    private var profileSection: some View {
        HStack(spacing: horizontalSizeClass == .regular ? 20 : 16) { // More spacing on iPad
            Circle()
                .fill(Color.blue.gradient)
                .overlay(Text("FG").font(horizontalSizeClass == .regular ? .largeTitle : .title2).fontWeight(.semibold).foregroundColor(.white))
                .frame(width: horizontalSizeClass == .regular ? 80 : 60, height: horizontalSizeClass == .regular ? 80 : 60)
                .clipShape(Circle())
            
            VStack(alignment: .leading, spacing: horizontalSizeClass == .regular ? 6 : 4) {
                Text("John Doe")
                    .font(horizontalSizeClass == .regular ? .title : .headline) // Larger name on iPad
                    .fontWeight(.medium)
                
                Text("john.doe@example.com")
                    .font(horizontalSizeClass == .regular ? .headline : .subheadline) // Larger email on iPad
                    .foregroundColor(.secondary)
                
                Button("Login / Sign Up") { // Changed button text
                    showingLoginView = true   // Present LoginView
                }
                .font(horizontalSizeClass == .regular ? .body : .caption) // Larger button text on iPad
                .foregroundColor(.accentColor) // Use accent color for actions
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
                Label("Account Status", systemImage: "crown.fill").foregroundColor(.orange)
                Spacer()
                VStack(alignment: .trailing, spacing: 2) {
                    Text("Genius Pro").font(.subheadline).fontWeight(.semibold).foregroundColor(.orange)
                    Text("Premium").font(.caption).foregroundColor(.secondary)
                }
            }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4) // Adaptive padding

            HStack {
                Label("Manage Subscription", systemImage: "creditcard").foregroundColor(.accentColor)
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
            integrationRow(title: "ESPN Fantasy", subtitle: "Connected", icon: "sportscourt.fill", iconColor: .red, isConnected: true)
                .onTapGesture { // Modified onTapGesture
                    showingESPNLoginWebView = true
                }
            integrationRow(title: "Yahoo Fantasy", subtitle: "Not Connected", icon: "y.circle.fill", iconColor: .purple, isConnected: false)
            integrationRow(title: "Sleeper", subtitle: "Not Connected", icon: "moon.zzz.fill", iconColor: .indigo, isConnected: false)
            
            HStack {
                Label("Add Integration", systemImage: "plus.circle.fill").foregroundColor(.accentColor)
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Add integration action */ }
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
                Text(title) // Font applied by Group
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
                Label("Monthly Usage", systemImage: "chart.bar.fill").foregroundColor(.accentColor)
                Spacer()
                VStack(alignment: .trailing, spacing: 2) {
                    Text("847 / 1000").font(.subheadline).fontWeight(.medium)
                    Text("Queries Used").font(.caption).foregroundColor(.secondary)
                }
            }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label("Usage History", systemImage: "calendar").foregroundColor(.accentColor)
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Usage history action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label("Reset Usage", systemImage: "arrow.clockwise.circle.fill").foregroundColor(.orange)
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Reset usage action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)
        }
        .font(horizontalSizeClass == .regular ? .headline : .body)
    }
    
    // MARK: - Preferences Section
    private var preferencesSection: some View {
        Group {
            HStack {
                Label("Notifications", systemImage: "bell.fill").foregroundColor(.red)
                Spacer()
                Toggle("", isOn: $isNotificationsEnabled).labelsHidden()
                    .scaleEffect(horizontalSizeClass == .regular ? 1.0 : 0.9) // Adjust toggle size
            }
            .padding(.vertical, horizontalSizeClass == .regular ? 4 : 2)

            HStack {
                Label("Dark Mode", systemImage: "moon.fill").foregroundColor(.indigo)
                Spacer()
                Toggle("", isOn: $isDarkModeEnabled).labelsHidden()
                    .scaleEffect(horizontalSizeClass == .regular ? 1.0 : 0.9)
            }
            .padding(.vertical, horizontalSizeClass == .regular ? 4 : 2)

            HStack {
                Label("Privacy Settings", systemImage: "hand.raised.fill").foregroundColor(.purple)
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Privacy settings action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)
        }
        .font(horizontalSizeClass == .regular ? .headline : .body)
    }
    
    // MARK: - About Section
    private var aboutSection: some View {
        Group {
            HStack {
                Label("Version", systemImage: "info.circle.fill").foregroundColor(.accentColor)
                Spacer()
                Text("1.0.0 (Build 1)").font(.subheadline).foregroundColor(.secondary)
            }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label("What's New", systemImage: "sparkles").foregroundColor(.orange)
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* What's new action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label("Help & Support", systemImage: "questionmark.circle.fill").foregroundColor(.green)
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Help & support action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label("Privacy Policy", systemImage: "doc.text.fill").foregroundColor(.gray)
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(.secondary.opacity(0.7))
            }
            .contentShape(Rectangle())
            .onTapGesture { /* Privacy policy action */ }
            .padding(.vertical, horizontalSizeClass == .regular ? 6 : 4)

            HStack {
                Label("Terms of Service", systemImage: "doc.text.fill").foregroundColor(.gray)
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

#Preview {
    SettingsView(isPresented: .constant(true))
}