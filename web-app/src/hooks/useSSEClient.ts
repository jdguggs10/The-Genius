import { useCallback } from 'react';
import { logger } from '../utils/logger';

interface SSEEvent {
  type: string;
  data: any;
}

interface SSEClientOptions {
  onEvent: (event: SSEEvent) => void;
  onError: (error: Error) => void;
  onComplete: () => void;
  // Timeout configuration (optional)
  connectionTimeoutMs?: number; // Timeout for initial connection
  streamTimeoutMs?: number;     // Timeout for stream inactivity
}

// Default timeout values
const DEFAULT_CONNECTION_TIMEOUT = 30000; // 30 seconds for initial connection
const DEFAULT_STREAM_TIMEOUT = 120000;    // 2 minutes for stream inactivity

export function useSSEClient() {
  const streamSSEResponse = useCallback(async (
    url: string,
    requestBody: any,
    options: SSEClientOptions
  ) => {
    const { 
      onEvent, 
      onError, 
      onComplete,
      connectionTimeoutMs = DEFAULT_CONNECTION_TIMEOUT,
      streamTimeoutMs = DEFAULT_STREAM_TIMEOUT
    } = options;
    
    logger.debug('🚀 Starting SSE request to:', url);
    logger.debug('📤 Request body:', requestBody);
    logger.debug('⏰ Timeouts - Connection:', connectionTimeoutMs, 'ms, Stream:', streamTimeoutMs, 'ms');
    
    let abortController: AbortController | null = null;
    let connectionTimeoutId: ReturnType<typeof setTimeout> | null = null;
    let streamTimeoutId: ReturnType<typeof setTimeout> | null = null;
    
    const cleanup = () => {
      if (connectionTimeoutId) {
        clearTimeout(connectionTimeoutId);
        connectionTimeoutId = null;
      }
      if (streamTimeoutId) {
        clearTimeout(streamTimeoutId);
        streamTimeoutId = null;
      }
      if (abortController && !abortController.signal.aborted) {
        abortController.abort();
      }
    };

    const createTimeoutError = (type: 'connection' | 'stream') => {
      const message = type === 'connection' 
        ? `Connection timeout: Server did not respond within ${connectionTimeoutMs / 1000}s`
        : `Stream timeout: No data received for ${streamTimeoutMs / 1000}s`;
      const error = new Error(message);
      error.name = 'TimeoutError';
      return error;
    };

    const resetStreamTimeout = () => {
      if (streamTimeoutId) {
        clearTimeout(streamTimeoutId);
      }
      streamTimeoutId = setTimeout(() => {
        logger.warn('⏰ Stream timeout - no data received within', streamTimeoutMs, 'ms');
        cleanup();
        onError(createTimeoutError('stream'));
      }, streamTimeoutMs);
    };
    
    try {
      abortController = new AbortController();
      
      // Set connection timeout
      connectionTimeoutId = setTimeout(() => {
        logger.warn('⏰ Connection timeout - server did not respond within', connectionTimeoutMs, 'ms');
        cleanup();
        onError(createTimeoutError('connection'));
      }, connectionTimeoutMs);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache'
        },
        body: JSON.stringify(requestBody),
        signal: abortController.signal
      });

      // Clear connection timeout since we got a response
      if (connectionTimeoutId) {
        clearTimeout(connectionTimeoutId);
        connectionTimeoutId = null;
      }

      logger.debug('📡 Response status:', response.status, response.statusText);
      logger.debug('📡 Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Unknown error');
        throw new Error(`Backend returned ${response.status}: ${response.statusText}. ${errorText}`);
      }

      if (!response.body) {
        throw new Error('No response body received');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let buffer = '';
      let currentEventType: string | null = null;
      let currentData: string | null = null;

      // Start stream timeout after connection is established
      resetStreamTimeout();

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            logger.debug('🏁 SSE stream completed');
            break;
          }

          // Reset stream timeout on each chunk received
          resetStreamTimeout();

          // Add new chunk to buffer
          const chunk = decoder.decode(value, { stream: true });
          logger.debug('📥 Received chunk:', JSON.stringify(chunk));
          buffer += chunk;
          
          // Process complete lines
          const lines = buffer.split('\n');
          // Keep the last (potentially incomplete) line in buffer
          buffer = lines.pop() || '';

          for (const line of lines) {
            logger.debug('📝 Processing line:', JSON.stringify(line));
            
            if (line.trim() === '') {
              // Empty line - process current event if we have both type and data
              if (currentEventType && currentData !== null) {
                try {
                  const parsedData = currentData ? JSON.parse(currentData) : {};
                  logger.debug('✅ Parsed SSE event:', currentEventType, parsedData);
                  onEvent({
                    type: currentEventType,
                    data: parsedData
                  });
                } catch (parseError) {
                  logger.warn('Failed to parse SSE event data:', currentData, 'Error:', parseError);
                  // Continue processing other events instead of throwing
                }
                
                // Reset for next event
                currentEventType = null;
                currentData = null;
              }
              continue;
            }

            const eventTypeMatch = line.match(/^event:\s*(.*)$/);
            if (eventTypeMatch) {
              currentEventType = eventTypeMatch[1].trim();
              logger.debug('🏷️  Event type:', currentEventType);
              continue;
            }
            
            if (line.startsWith('data: ')) {
              currentData = line.slice(6); // Remove 'data: ' prefix
              logger.debug('📊 Event data:', currentData);
              continue;
            }
            
            // Handle other SSE fields like id: or retry:
            if (line.startsWith('id: ') || line.startsWith('retry: ')) {
              logger.debug('📋 SSE metadata:', line);
              continue;
            }
          }
        }

        // Process any remaining event in buffer
        if (currentEventType && currentData !== null) {
          try {
            const parsedData = currentData ? JSON.parse(currentData) : {};
            logger.debug('✅ Final SSE event:', currentEventType, parsedData);
            onEvent({
              type: currentEventType,
              data: parsedData
            });
          } catch (parseError) {
            logger.warn('Failed to parse final SSE event data:', currentData, 'Error:', parseError);
          }
        }

        // Clear stream timeout on successful completion
        if (streamTimeoutId) {
          clearTimeout(streamTimeoutId);
          streamTimeoutId = null;
        }

        onComplete();
        
      } finally {
        reader.releaseLock();
      }
      
    } catch (error) {
      // Don't log aborted requests as errors unless they were timeout aborts
      if (error instanceof Error && error.name === 'AbortError') {
        // Check if this was a timeout abort or user abort
        if (!connectionTimeoutId && !streamTimeoutId) {
          logger.info('📡 SSE request was aborted');
          return;
        }
        // If timeouts are still active, this might be a timeout abort
        logger.warn('📡 SSE request was aborted (possibly timeout)');
        return;
      }
      
      // Handle timeout errors specifically
      if (error instanceof Error && error.name === 'TimeoutError') {
        logger.error('⏰ SSE timeout error:', error.message);
        onError(error);
        return;
      }
      
      logger.error('❌ SSE streaming error:', error);
      onError(error instanceof Error ? error : new Error(String(error)));
    } finally {
      // Clean up all timeouts and abort controller
      cleanup();
    }
  }, []);

  return { streamSSEResponse };
} 