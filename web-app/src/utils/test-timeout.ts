// Test utility to demonstrate timeout handling
// This file can be used for manual testing of timeout scenarios

import { logger } from './logger';

/**
 * Creates a mock SSE response that simulates different timeout scenarios
 * for testing the timeout handling functionality
 */
export const createTimeoutTestResponse = (scenario: 'connection' | 'stream' | 'success') => {
  return new Response(
    new ReadableStream({
      start(controller) {
        logger.debug('🧪 Starting timeout test scenario:', scenario);
        
        if (scenario === 'connection') {
          // Simulate connection timeout - never send any data
          // The connection timeout should trigger
          return;
        }
        
        if (scenario === 'stream') {
          // Send initial data then stop - stream timeout should trigger
          controller.enqueue(new TextEncoder().encode('event: status_update\ndata: {"status": "created"}\n\n'));
          // Don't send any more data - stream timeout will occur
          return;
        }
        
        if (scenario === 'success') {
          // Simulate successful response
          const messages = [
            'event: status_update\ndata: {"status": "created"}\n\n',
            'event: text_delta\ndata: {"delta": "Hello"}\n\n',
            'event: text_delta\ndata: {"delta": " world"}\n\n',
            'event: response_complete\ndata: {"status": "complete", "final_json": {"main_advice": "Hello world"}}\n\n'
          ];
          
          let index = 0;
          const sendNext = () => {
            if (index < messages.length) {
              controller.enqueue(new TextEncoder().encode(messages[index]));
              index++;
              setTimeout(sendNext, 100); // Small delay between messages
            } else {
              controller.close();
            }
          };
          
          sendNext();
        }
      }
    }),
    {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache'
      }
    }
  );
};

/**
 * Manual test function to verify timeout scenarios
 * Can be called from browser console in development
 */
export const testTimeoutScenarios = async () => {
  if (!import.meta.env.DEV) {
    logger.warn('Timeout tests only available in development mode');
    return;
  }
  
  logger.essential('🧪 Starting timeout scenario tests...');
  logger.essential('These tests demonstrate timeout handling but will trigger actual timeouts');
  logger.essential('Check the console and UI for timeout error messages');
  
  // Note: These would need to be integrated with the actual SSE client
  // This is just a demonstration of the test utilities available
}; 