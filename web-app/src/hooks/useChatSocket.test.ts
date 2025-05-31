// web-app/src/hooks/useChatSocket.test.ts
import { renderHook, act } from '@testing-library/react';
import { useChatSocket, WebSocketState } from './useChatSocket';

// Mock WebSocket global
const mockSend = vi.fn();
const mockClose = vi.fn();
let mockWebSocketInstance: {
    readyState: number;
    onopen?: () => void;
    onmessage?: (event: any) => void;
    onerror?: (event?: any) => void; // Added optional event arg
    onclose?: (event: any) => void;
    send: typeof mockSend;
    close: typeof mockClose;
} | null = null;

global.WebSocket = vi.fn().mockImplementation((url) => {
  mockWebSocketInstance = {
    readyState: WebSocket.CONNECTING, // Initial state
    send: mockSend,
    close: mockClose,
  };
  // Simulate async connection: call onopen shortly after instance creation
  // This is a common pattern, but real WebSocket behavior can vary.
  setTimeout(() => {
    if (mockWebSocketInstance && mockWebSocketInstance.onopen && mockWebSocketInstance.readyState === WebSocket.CONNECTING) {
      mockWebSocketInstance.readyState = WebSocket.OPEN;
      mockWebSocketInstance.onopen();
    }
  }, 0); // Use 0 for next tick
  return mockWebSocketInstance;
}) as any;

describe('useChatSocket', () => {
  const mockOnOpen = vi.fn();
  const mockOnMessage = vi.fn();
  const mockOnError = vi.fn();
  const mockOnClose = vi.fn();
  const mockOnRetrying = vi.fn();
  const testUrl = 'ws://localhost:8080';

  beforeEach(() => {
    vi.clearAllMocks();
    mockWebSocketInstance = null; // Reset instance
    // Reset readyState for scenarios where WebSocket might not be "created" by the hook
    if (global.WebSocket.mockClear) global.WebSocket.mockClear();
  });

  it('should connect, send message, and disconnect', async () => {
    const { result } = renderHook(() => useChatSocket(testUrl, {
      onOpen: mockOnOpen,
      onMessage: mockOnMessage,
      onError: mockOnError,
      onClose: mockOnClose,
      onRetrying: mockOnRetrying,
    }));

    expect(result.current.socketState).toBe(WebSocketState.CLOSED); // Initial state

    act(() => {
      result.current.connect();
    });

    expect(result.current.socketState).toBe(WebSocketState.CONNECTING);

    // Wait for mocked async connection
    await vi.waitFor(() => expect(result.current.socketState).toBe(WebSocketState.OPEN), { timeout: 100 });
    expect(mockOnOpen).toHaveBeenCalled();

    act(() => {
      result.current.sendMessage({ conversation: [], enable_web_search: false });
    });
    expect(mockSend).toHaveBeenCalled();

    act(() => {
      result.current.disconnect();
    });
    expect(mockClose).toHaveBeenCalledWith(1000, "User disconnected");
    // Depending on how disconnect sets state, it might be CLOSING then CLOSED.
    // Check for one of these as the mock might resolve faster.
    expect([WebSocketState.CLOSING, WebSocketState.CLOSED]).toContain(result.current.socketState);
  });

  it('handles message parsing and calls onMessage', async () => {
    const { result } = renderHook(() => useChatSocket(testUrl, { onMessage: mockOnMessage }));
    act(() => { result.current.connect(); });
    await vi.waitFor(() => expect(result.current.socketState).toBe(WebSocketState.OPEN));

    const testMessage = { type: 'text_delta', data: { delta: 'Hello' } };
    act(() => {
      mockWebSocketInstance?.onmessage?.({ data: JSON.stringify(testMessage) });
    });
    expect(mockOnMessage).toHaveBeenCalledWith(testMessage);
  });

  it('handles reconnection on unexpected close', async () => {
    vi.useFakeTimers();
    const { result } = renderHook(() => useChatSocket(testUrl, {
        onClose: mockOnClose,
        onRetrying: mockOnRetrying,
        onError: mockOnError
    }));

    act(() => { result.current.connect(); });
    await vi.waitFor(() => expect(result.current.socketState).toBe(WebSocketState.OPEN));

    // Simulate unexpected close
    act(() => {
      mockWebSocketInstance?.onclose?.({ wasClean: false, code: 1006, reason: 'Network error' });
    });

    expect(mockOnClose).toHaveBeenCalled();
    expect(result.current.socketState).toBe(WebSocketState.RECONNECTING);
    expect(mockOnRetrying).toHaveBeenCalledWith(1); // First retry attempt

    // Fast-forward timers to trigger reconnect attempt
    // WebSocket mock will be called again due to connect() in retry
    act(() => {
        vi.advanceTimersByTime(1000);
    });

    // It should attempt to connect again, leading to CONNECTING then OPEN
    await vi.waitFor(() => expect(result.current.socketState).toBe(WebSocketState.OPEN));

    vi.useRealTimers();
  });

   it('calls onError if WebSocket creation fails and max retries are reached', async () => {
    vi.useFakeTimers();
    // Make WebSocket constructor throw an error
    (global.WebSocket as vi.Mock).mockImplementation(() => {
        throw new Error("Connection failed");
    });

    const { result } = renderHook(() => useChatSocket(testUrl, { onError: mockOnError, onRetrying: mockOnRetrying }));

    act(() => { result.current.connect(); });

    // It will try to reconnect MAX_RECONNECT_ATTEMPTS times
    for (let i = 1; i <= 5; i++) {
        expect(result.current.socketState).toBe(WebSocketState.RECONNECTING);
        expect(mockOnRetrying).toHaveBeenCalledWith(i);
        act(() => { vi.advanceTimersByTime(1000 * Math.pow(2, i)); }); // Advance by current delay
    }

    // After max retries, it should call onError and be in CLOSED state
    expect(mockOnError).toHaveBeenCalledWith(expect.stringContaining("Failed to create WebSocket and max retries reached."));
    expect(result.current.socketState).toBe(WebSocketState.CLOSED);

    vi.useRealTimers();
    // Restore original WebSocket mock for other tests
    (global.WebSocket as vi.Mock).mockImplementation((url) => {
      mockWebSocketInstance = { readyState: WebSocket.CONNECTING, send: mockSend, close: mockClose };
      setTimeout(() => {
        if (mockWebSocketInstance && mockWebSocketInstance.onopen) {
          mockWebSocketInstance.readyState = WebSocket.OPEN;
          mockWebSocketInstance.onopen();
        }
      }, 0);
      return mockWebSocketInstance;
    });
  });


});
