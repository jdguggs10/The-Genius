//
//  SettingsView.swift
//  ios-app
//
//  Created by Gerald Gugger on 5/14/25.
//
import SwiftUI

struct SettingsView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var isNotificationsEnabled = true
    @State private var isDarkModeEnabled = false
    
    var body: some View {
        NavigationStack {
            List {
                // Profile Section
                Section {
                    profileSection
                } header: {
                    Text("Profile")
                }
                
                // Account Section
                Section {
                    accountSection
                } header: {
                    Text("Account")
                }
                
                // Integrations Section
                Section {
                    integrationsSection
                } header: {
                    Text("Integrations")
                }
                
                // Usage Section
                Section {
                    usageSection
                } header: {
                    Text("Usage")
                }
                
                // Preferences Section
                Section {
                    preferencesSection
                } header: {
                    Text("Preferences")
                }
                
                // About Section
                Section {
                    aboutSection
                } header: {
                    Text("About The Genius")
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
    
    // MARK: - Profile Section
    private var profileSection: some View {
        HStack(spacing: 16) {
            // Profile Picture
            AsyncImage(url: URL(string: "https://via.placeholder.com/60x60/007AFF/FFFFFF?text=FG")) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Circle()
                    .fill(.blue.gradient)
                    .overlay {
                        Text("FG")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                    }
            }
            .frame(width: 60, height: 60)
            .clipShape(Circle())
            
            VStack(alignment: .leading, spacing: 4) {
                Text("John Doe")
                    .font(.headline)
                    .fontWeight(.medium)
                
                Text("john.doe@example.com")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                Button("Edit Profile") {
                    // Edit profile action
                }
                .font(.caption)
                .foregroundColor(.blue)
            }
            
            Spacer()
        }
        .padding(.vertical, 8)
    }
    
    // MARK: - Account Section
    private var accountSection: some View {
        VStack(spacing: 0) {
            HStack {
                Label("Account Status", systemImage: "crown.fill")
                    .foregroundColor(.orange)
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 2) {
                    Text("Genius Pro")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundColor(.orange)
                    
                    Text("Premium")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.vertical, 12)
            
            Divider()
            
            HStack {
                Label("Manage Subscription", systemImage: "creditcard")
                    .foregroundColor(.blue)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .padding(.vertical, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                // Manage subscription action
            }
        }
    }
    
    // MARK: - Integrations Section
    private var integrationsSection: some View {
        VStack(spacing: 0) {
            integrationRow(
                title: "ESPN Fantasy",
                subtitle: "Connected",
                icon: "sportscourt",
                iconColor: .red,
                isConnected: true
            )
            
            Divider()
                .padding(.leading, 44)
            
            integrationRow(
                title: "Yahoo Fantasy",
                subtitle: "Not Connected",
                icon: "y.circle",
                iconColor: .purple,
                isConnected: false
            )
            
            Divider()
                .padding(.leading, 44)
            
            integrationRow(
                title: "Sleeper",
                subtitle: "Not Connected",
                icon: "moon.zzz",
                iconColor: .indigo,
                isConnected: false
            )
            
            Divider()
                .padding(.leading, 44)
            
            HStack {
                Label("Add Integration", systemImage: "plus.circle")
                    .foregroundColor(.blue)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .padding(.vertical, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                // Add integration action
            }
        }
    }
    
    private func integrationRow(title: String, subtitle: String, icon: String, iconColor: Color, isConnected: Bool) -> some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(iconColor)
                .frame(width: 20)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.body)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(isConnected ? .green : .secondary)
            }
            
            Spacer()
            
            if isConnected {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.green)
            } else {
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
        }
        .padding(.vertical, 12)
        .contentShape(Rectangle())
        .onTapGesture {
            // Integration management action
        }
    }
    
    // MARK: - Usage Section
    private var usageSection: some View {
        VStack(spacing: 0) {
            HStack {
                Label("Monthly Usage", systemImage: "chart.bar")
                    .foregroundColor(.blue)
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 2) {
                    Text("847 / 1000")
                        .font(.subheadline)
                        .fontWeight(.medium)
                    
                    Text("Queries Used")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.vertical, 12)
            
            Divider()
            
            HStack {
                Label("Usage History", systemImage: "calendar")
                    .foregroundColor(.green)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .padding(.vertical, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                // Usage history action
            }
            
            Divider()
            
            HStack {
                Label("Reset Usage", systemImage: "arrow.clockwise")
                    .foregroundColor(.orange)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .padding(.vertical, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                // Reset usage action
            }
        }
    }
    
    // MARK: - Preferences Section
    private var preferencesSection: some View {
        VStack(spacing: 0) {
            HStack {
                Label("Notifications", systemImage: "bell")
                    .foregroundColor(.red)
                
                Spacer()
                
                Toggle("", isOn: $isNotificationsEnabled)
            }
            .padding(.vertical, 12)
            
            Divider()
            
            HStack {
                Label("Dark Mode", systemImage: "moon")
                    .foregroundColor(.indigo)
                
                Spacer()
                
                Toggle("", isOn: $isDarkModeEnabled)
            }
            .padding(.vertical, 12)
            
            Divider()
            
            HStack {
                Label("Privacy Settings", systemImage: "hand.raised")
                    .foregroundColor(.purple)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .padding(.vertical, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                // Privacy settings action
            }
        }
    }
    
    // MARK: - About Section
    private var aboutSection: some View {
        VStack(spacing: 0) {
            HStack {
                Label("Version", systemImage: "info.circle")
                    .foregroundColor(.blue)
                
                Spacer()
                
                Text("1.0.0 (Build 1)")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .padding(.vertical, 12)
            
            Divider()
            
            HStack {
                Label("What's New", systemImage: "sparkles")
                    .foregroundColor(.orange)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .padding(.vertical, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                // What's new action
            }
            
            Divider()
            
            HStack {
                Label("Help & Support", systemImage: "questionmark.circle")
                    .foregroundColor(.green)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .padding(.vertical, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                // Help & support action
            }
            
            Divider()
            
            HStack {
                Label("Privacy Policy", systemImage: "doc.text")
                    .foregroundColor(.gray)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .padding(.vertical, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                // Privacy policy action
            }
            
            Divider()
            
            HStack {
                Label("Terms of Service", systemImage: "doc.text")
                    .foregroundColor(.gray)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
                    .font(.caption)
            }
            .padding(.vertical, 12)
            .contentShape(Rectangle())
            .onTapGesture {
                // Terms of service action
            }
        }
    }
}

#Preview {
    SettingsView()
}