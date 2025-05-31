// web-app/src/hooks/useChatSocket.ts
import { useCallback, useEffect, useRef, useState } from 'react';
import type { AdviceRequest, SSEEventData } from '../types';
import { logger } from '../utils/logger';

export enum WebSocketState {
  CONNECTING,
  OPEN,
  CLOSING,
  CLOSED,
  RECONNECTING,
}

interface ChatSocketOptions {
  onOpen?: (event: Event) => void;
  onMessage: (eventData: SSEEventData) => void;
  onError?: (errorMessage: string) => void;
  onClose?: (event: CloseEvent) => void;
  onRetrying?: (attempt: number) => void;
}

const MAX_RECONNECT_ATTEMPTS = 5;
const INITIAL_RECONNECT_INTERVAL = 1000; // ms

export function useChatSocket(socketUrl: string, options: ChatSocketOptions) {
  const { onOpen, onMessage, onError, onClose, onRetrying } = options;
  const ws = useRef<WebSocket | null>(null);
  const [socketState, setSocketState] = useState<WebSocketState>(WebSocketState.CLOSED);
  const reconnectAttempts = useRef(0);
  const explicitlyClosed = useRef(false);
  const reconnectTimeoutId = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (ws.current && (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    explicitlyClosed.current = false;
    setSocketState(WebSocketState.CONNECTING);
    if (reconnectAttempts.current > 0 && onRetrying) {
      onRetrying(reconnectAttempts.current);
    }

    try {
      ws.current = new WebSocket(socketUrl);

      ws.current.onopen = (event) => {
        setSocketState(WebSocketState.OPEN);
        reconnectAttempts.current = 0;
        if (reconnectTimeoutId.current) clearTimeout(reconnectTimeoutId.current);
        if (onOpen) onOpen(event);
      };

      ws.current.onmessage = (event) => {
        try {
          const parsedData: SSEEventData = JSON.parse(event.data as string);
          onMessage(parsedData);
        } catch (e) {
          logger.error('Failed to parse WebSocket message:', e);
          if (onError) onError(`Failed to parse message: ${e instanceof Error ? e.message : String(e)}`);
        }
      };

      ws.current.onerror = (event) => {
        logger.error('WebSocket network error (will be followed by onclose):', event);
      };

      ws.current.onclose = (event) => {
        const closeReason = event.wasClean ? `WebSocket closed cleanly, code=${event.code} reason=${event.reason}` : `WebSocket connection problem, code=${event.code} reason=${event.reason}`;
        setSocketState(WebSocketState.CLOSED); // Set to CLOSED first
        if (onClose) onClose(event); // Call onClose callback to inform consumer

        if (!explicitlyClosed.current && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current++;
          setSocketState(WebSocketState.RECONNECTING); // Then set to RECONNECTING if applicable
          const delay = INITIAL_RECONNECT_INTERVAL * Math.pow(2, reconnectAttempts.current - 1);
          if (reconnectTimeoutId.current) clearTimeout(reconnectTimeoutId.current);
          reconnectTimeoutId.current = setTimeout(connect, delay);
        } else if (!explicitlyClosed.current && reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
          logger.error("Max reconnection attempts reached.");
          if (onError) onError(`Max reconnection attempts reached. ${closeReason}`);
        }
      };
    } catch (error) {
        logger.error("Error creating WebSocket:", error);
        const errorMsg = `Error creating WebSocket: ${error instanceof Error ? error.message : String(error)}`;
        if (onError) onError(errorMsg);
        setSocketState(WebSocketState.CLOSED);
        // Attempt to reconnect even if WebSocket creation itself fails
        if (!explicitlyClosed.current && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current++;
          setSocketState(WebSocketState.RECONNECTING);
          const delay = INITIAL_RECONNECT_INTERVAL * Math.pow(2, reconnectAttempts.current - 1);
          if (reconnectTimeoutId.current) clearTimeout(reconnectTimeoutId.current);
          reconnectTimeoutId.current = setTimeout(connect, delay);
        } else if (!explicitlyClosed.current) { // Max attempts reached for creation
             if (onError) onError(`Failed to create WebSocket and max retries reached. ${errorMsg}`);
        }
    }
  }, [socketUrl, onOpen, onMessage, onError, onClose, onRetrying]);

  const disconnect = useCallback(() => {
    explicitlyClosed.current = true;
    if (reconnectTimeoutId.current) {
        clearTimeout(reconnectTimeoutId.current);
        reconnectTimeoutId.current = null;
    }
    if (ws.current) {
      if (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING) {
        setSocketState(WebSocketState.CLOSING);
        ws.current.close(1000, "User disconnected");
      } else {
         // If already closing or closed, ensure state reflects finality if not already CLOSING
         if(ws.current.readyState !== WebSocket.CLOSING) setSocketState(WebSocketState.CLOSED);
      }
    } else {
        setSocketState(WebSocketState.CLOSED); // No instance, so it's closed
    }
  }, []);

  const sendMessage = useCallback((data: AdviceRequest) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      try {
        ws.current.send(JSON.stringify(data));
      } catch (e) {
        logger.error('Failed to send message via WebSocket:', e);
        if (onError) onError(`Failed to send message: ${e instanceof Error ? e.message : String(e)}`);
      }
    } else {
      if (onError) onError('WebSocket not open. Cannot send message. Please try sending again or wait for reconnection.');
    }
  }, [onError]);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      explicitlyClosed.current = true; // Ensure no reconnections on unmount
      if (reconnectTimeoutId.current) {
        clearTimeout(reconnectTimeoutId.current);
        reconnectTimeoutId.current = null;
      }
      if (ws.current && (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING)) {
        ws.current.close(1000, "Component unmounted");
      }
      setSocketState(WebSocketState.CLOSED);
    };
  }, []); // Empty dependency array means this runs once on mount and cleanup on unmount

  return { connect, disconnect, sendMessage, socketState, WebSocketState };
}
