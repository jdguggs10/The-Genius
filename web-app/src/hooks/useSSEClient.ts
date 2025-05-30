import { useCallback } from 'react';

interface SSEEvent {
  type: string;
  data: any;
}

interface SSEClientOptions {
  onEvent: (event: SSEEvent) => void;
  onError: (error: Error) => void;
  onComplete: () => void;
}

export function useSSEClient() {
  const streamSSEResponse = useCallback(async (
    url: string,
    requestBody: any,
    options: SSEClientOptions
  ) => {
    const { onEvent, onError, onComplete } = options;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response body received');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let buffer = '';
      let currentEventType: string | null = null;
      let currentData: string | null = null;

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // Add new chunk to buffer
          buffer += decoder.decode(value, { stream: true });
          
          // Process complete lines
          const lines = buffer.split('\n');
          // Keep the last (potentially incomplete) line in buffer
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.trim() === '') {
              // Empty line - process current event if we have both type and data
              if (currentEventType && currentData !== null) {
                try {
                  const parsedData = currentData ? JSON.parse(currentData) : {};
                  onEvent({
                    type: currentEventType,
                    data: parsedData
                  });
                } catch (parseError) {
                  console.warn('Failed to parse SSE event data:', currentData, 'Error:', parseError);
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
              continue;
            }
            
            if (line.startsWith('data: ')) {
              currentData = line.slice(6); // Remove 'data: ' prefix
              continue;
            }
          }
        }

        // Process any remaining event in buffer
        if (currentEventType && currentData !== null) {
          try {
            const parsedData = currentData ? JSON.parse(currentData) : {};
            onEvent({
              type: currentEventType,
              data: parsedData
            });
          } catch (parseError) {
            console.warn('Failed to parse final SSE event data:', currentData, 'Error:', parseError);
          }
        }

        onComplete();
        
      } finally {
        reader.releaseLock();
      }
      
    } catch (error) {
      console.error('SSE streaming error:', error);
      onError(error instanceof Error ? error : new Error(String(error)));
    }
  }, []);

  return { streamSSEResponse };
} 