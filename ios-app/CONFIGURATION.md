# iOS App Configuration Guide

## Automatic Backend Configuration

Your iOS app now uses the `ApiConfiguration.swift` file to manage backend URLs automatically.

## Current Setup

By default, the app is configured to use the **production backend** (`https://genius-backend-nhl3.onrender.com`) for both Debug and Release builds.

## Switching to Local Development Backend

To test against your local backend running on `localhost:8000`:

### Option 1: Quick Toggle (Recommended)
1. Open `ApiConfiguration.swift`
2. In the `getBackendBaseURL()` method, uncomment this line:
   ```swift
   return localBackendURL
   ```
3. Comment out this line:
   ```swift
   // return productionBackendURL
   ```

### Option 2: Environment-Based Switching
The configuration is already set up to easily switch based on build configuration:

```swift
#if DEBUG
return localBackendURL  // Use local backend in debug builds
#else
return productionBackendURL  // Use production in release builds
#endif
```

## No More Manual Switching!

With this setup:

1. **Development Testing**: Uncomment local backend line in `ApiConfiguration.swift`
2. **Production/TestFlight**: Comment out local backend, use production URL
3. **Debugging**: Check Xcode console for API configuration logs when sending messages

## Configuration Logging

When you send a message, you'll see logs in Xcode console like:
```
🔧 iOS API Configuration:
   Environment: DEBUG
   Backend Base URL: https://genius-backend-nhl3.onrender.com
   Advice URL: https://genius-backend-nhl3.onrender.com/advice
   Health URL: https://genius-backend-nhl3.onrender.com/health
```

## Advanced Configuration

You can also:

- Add build configuration variables
- Use different URLs for different schemes
- Implement runtime URL switching in the app UI

The `ApiConfiguration.swift` file provides helper methods for all these scenarios. 