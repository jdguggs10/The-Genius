/**
 * API Configuration Utility
 * Automatically handles local vs production backend URLs
 */

const isDevelopment = import.meta.env.DEV;

// Default production backend URL
const PRODUCTION_BACKEND_URL = 'https://genius-backend-nhl3.onrender.com';

// Local development backend URL  
const LOCAL_BACKEND_URL = 'http://localhost:8000';

/**
 * Get the appropriate API base URL based on environment
 * In development: uses proxy (/api) for local backend, or explicit URL if overridden
 * In production: uses explicit backend URL or falls back to default
 */
export function getApiBaseUrl(): string {
  if (isDevelopment) {
    // If VITE_BACKEND_URL is explicitly set in development, use it directly
    // Otherwise use the proxy path '/api' which Vite will redirect to localhost:8000
    const explicitUrl = import.meta.env.VITE_BACKEND_URL;
    if (explicitUrl && explicitUrl !== LOCAL_BACKEND_URL) {
      return explicitUrl;
    }
    return '/api';
  }
  
  // In production, use explicit backend URL or fallback
  return import.meta.env.VITE_BACKEND_URL || PRODUCTION_BACKEND_URL;
}

/**
 * Get the full URL for a specific endpoint
 */
export function getApiUrl(endpoint: string): string {
  const baseUrl = getApiBaseUrl();
  const cleanBase = baseUrl.replace(/\/$/, '');
  const cleanEndpoint = endpoint.replace(/^\//, '');
  return `${cleanBase}/${cleanEndpoint}`;
}

/**
 * Get health check URL for testing connectivity
 */
export function getHealthUrl(): string {
  return getApiUrl('health');
}

/**
 * Get advice endpoint URL
 */
export function getAdviceUrl(): string {
  return getApiUrl('advice');
}

/**
 * Get model endpoint URL
 */
export function getModelUrl(): string {
  return getApiUrl('model');
}

/**
 * Get default model setting URL
 */
export function getDefaultModelSettingUrl(): string {
  return getApiUrl('settings/default-model');
}

/**
 * Log current API configuration (useful for debugging)
 */
export function logApiConfig(): void {
  console.log('🔧 API Configuration:', {
    environment: isDevelopment ? 'development' : 'production',
    baseUrl: getApiBaseUrl(),
    explicit_override: import.meta.env.VITE_BACKEND_URL,
    health_url: getHealthUrl(),
    advice_url: getAdviceUrl(),
  });
} 