//
//  ApiConfiguration.swift
//  ios-app
//
//  Auto-generated API configuration
//

import Foundation

struct ApiConfiguration {
    
    // MARK: - Environment Detection
    
    #if DEBUG
    static let isDebug = true
    #else
    static let isDebug = false
    #endif
    
    // MARK: - Backend URLs
    
    private static let localBackendURL = "http://localhost:8000"
    private static let productionBackendURL = "https://genius-backend-nhl3.onrender.com"
    
    // MARK: - Configuration Methods
    
    /// Get the appropriate backend base URL based on environment and configuration
    static func getBackendBaseURL() -> String {
        // Check if we have a custom URL set via build configuration or environment
        // For now, we default to production URL for both debug and release
        // You can modify this logic as needed
        
        #if DEBUG
        // In debug mode, you can uncomment the next line to use local backend
        // return localBackendURL
        return productionBackendURL
        #else
        return productionBackendURL
        #endif
    }
    
    /// Get the full advice endpoint URL
    static func getAdviceURL() -> String {
        return "\(getBackendBaseURL())/advice"
    }
    
    /// Get the health check endpoint URL
    static func getHealthURL() -> String {
        return "\(getBackendBaseURL())/health"
    }
    
    /// Get the model endpoint URL
    static func getModelURL() -> String {
        return "\(getBackendBaseURL())/model"
    }
    
    /// Log current API configuration for debugging
    static func logConfiguration() {
        print("🔧 iOS API Configuration:")
        print("   Environment: \(isDebug ? "DEBUG" : "RELEASE")")
        print("   Backend Base URL: \(getBackendBaseURL())")
        print("   Advice URL: \(getAdviceURL())")
        print("   Health URL: \(getHealthURL())")
    }
    
    // MARK: - Local Development Helpers
    
    /// Check if backend is using localhost
    static var isUsingLocalBackend: Bool {
        return getBackendBaseURL().contains("localhost")
    }
    
    /// Manual override for local development (call this method to switch to local backend)
    static func useLocalBackend() -> String {
        return localBackendURL
    }
    
    /// Manual override for production backend
    static func useProductionBackend() -> String {
        return productionBackendURL
    }
} 