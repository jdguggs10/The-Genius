// web-app/src/components/chat.test.tsx
import { render, screen, cleanup, fireEvent, waitFor, act } from '@testing-library/react';
import { vi, beforeEach, afterEach, describe, it, expect } from 'vitest';
import Chat from './chat';

// Mock the hooks with proper module paths
vi.mock('../hooks/useConversationManager', () => ({
  useConversationManager: vi.fn(() => ({
    messages: [],
    lastResponseId: null,
    addMessage: vi.fn(),
    updateMessage: vi.fn(),
    setLastResponseId: vi.fn(),
    getConversationForAPI: vi.fn(() => [])
  }))
}));

vi.mock('../hooks/useSSEClient', () => ({
  useSSEClient: vi.fn(() => ({
    streamSSEResponse: vi.fn()
  }))
}));

// Mock environment variables
vi.stubGlobal('importMeta', {
  env: {
    VITE_BACKEND_URL: 'http://localhost:8000',
  },
});

// Mock fetch for API calls
global.fetch = vi.fn() as any;

// Mock DOM methods that don't exist in test environment
const mockScrollIntoView = vi.fn();
beforeEach(() => {
  Object.defineProperty(Element.prototype, 'scrollIntoView', {
    value: mockScrollIntoView,
    writable: true,
  });
});

describe('Chat Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    const mockFetch = global.fetch as any;
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ model: 'GPT-4.1' })
    });
  });

  afterEach(() => {
    cleanup();
  });

  it('renders the chat interface correctly', () => {
    render(<Chat />);
    
    // Check for key elements - use more specific selectors
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ask about fantasy sports...')).toBeInTheDocument();
  });

  it('fetches the default model on mount', async () => {
    await act(async () => {
      render(<Chat />);
    });
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/model')
      );
    });
  });

  it('shows conversation active indicator when lastResponseId exists', () => {
    const mockHookReturn = {
      messages: [],
      lastResponseId: 'test-response-id',
      addMessage: vi.fn(),
      updateMessage: vi.fn(),
      setLastResponseId: vi.fn(),
      getConversationForAPI: vi.fn(() => [])
    };

    const { useConversationManager } = require('../hooks/useConversationManager');
    useConversationManager.mockReturnValue(mockHookReturn);
    
    render(<Chat />);
    
    expect(screen.getByText('Conversation Active')).toBeInTheDocument();
  });

  it('calls streamSSEResponse when sending a message', async () => {
    const mockStreamSSEResponse = vi.fn();
    const mockAddMessage = vi.fn();
    
    const { useSSEClient } = require('../hooks/useSSEClient');
    const { useConversationManager } = require('../hooks/useConversationManager');
    
    useSSEClient.mockReturnValue({
      streamSSEResponse: mockStreamSSEResponse
    });
    
    useConversationManager.mockReturnValue({
      messages: [],
      lastResponseId: null,
      addMessage: mockAddMessage,
      updateMessage: vi.fn(),
      setLastResponseId: vi.fn(),
      getConversationForAPI: vi.fn(() => [])
    });

    render(<Chat />);
    
    const input = screen.getByPlaceholderText('Ask about fantasy sports...');
    const sendButton = screen.getByRole('button');
    
    await act(async () => {
      fireEvent.change(input, { target: { value: 'Who should I start this week?' } });
      fireEvent.click(sendButton);
    });
    
    // Verify that streamSSEResponse was called
    expect(mockStreamSSEResponse).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        conversation: expect.any(Array),
        enable_web_search: expect.any(Boolean)
      }),
      expect.objectContaining({
        onEvent: expect.any(Function),
        onError: expect.any(Function),
        onComplete: expect.any(Function)
      })
    );
  });

  it('includes previous_response_id in request when available', async () => {
    const mockStreamSSEResponse = vi.fn();
    
    const { useSSEClient } = require('../hooks/useSSEClient');
    const { useConversationManager } = require('../hooks/useConversationManager');
    
    useSSEClient.mockReturnValue({
      streamSSEResponse: mockStreamSSEResponse
    });
    
    useConversationManager.mockReturnValue({
      messages: [
        { role: 'user', content: 'First question', id: '1' },
        { role: 'assistant', content: 'First answer', id: '2' }
      ],
      lastResponseId: 'previous-response-id',
      addMessage: vi.fn(),
      updateMessage: vi.fn(),
      setLastResponseId: vi.fn(),
      getConversationForAPI: vi.fn(() => [
        { role: 'user', content: 'First question', id: '1' },
        { role: 'assistant', content: 'First answer', id: '2' }
      ])
    });

    render(<Chat />);
    
    const input = screen.getByPlaceholderText('Ask about fantasy sports...');
    const sendButton = screen.getByRole('button');
    
    await act(async () => {
      fireEvent.change(input, { target: { value: 'Follow-up question' } });
      fireEvent.click(sendButton);
    });
    
    // Verify that previous_response_id is included in the request
    expect(mockStreamSSEResponse).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        previous_response_id: 'previous-response-id'
      }),
      expect.any(Object)
    );
  });

  it('sends full conversation history when no previous_response_id', async () => {
    const mockStreamSSEResponse = vi.fn();
    const mockGetConversationForAPI = vi.fn(() => [
      { role: 'user', content: 'Previous question', id: '1' },
      { role: 'assistant', content: 'Previous answer', id: '2' }
    ]);
    
    const { useSSEClient } = require('../hooks/useSSEClient');
    const { useConversationManager } = require('../hooks/useConversationManager');
    
    useSSEClient.mockReturnValue({
      streamSSEResponse: mockStreamSSEResponse
    });
    
    useConversationManager.mockReturnValue({
      messages: [
        { role: 'user', content: 'Previous question', id: '1' },
        { role: 'assistant', content: 'Previous answer', id: '2' }
      ],
      lastResponseId: null,
      addMessage: vi.fn(),
      updateMessage: vi.fn(),
      setLastResponseId: vi.fn(),
      getConversationForAPI: mockGetConversationForAPI
    });

    render(<Chat />);
    
    const input = screen.getByPlaceholderText('Ask about fantasy sports...');
    const sendButton = screen.getByRole('button');
    
    await act(async () => {
      fireEvent.change(input, { target: { value: 'New question' } });
      fireEvent.click(sendButton);
    });
    
    // Verify that the full conversation is included
    expect(mockStreamSSEResponse).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        conversation: expect.arrayContaining([
          expect.objectContaining({ role: 'user', content: 'Previous question' }),
          expect.objectContaining({ role: 'assistant', content: 'Previous answer' }),
          expect.objectContaining({ role: 'user', content: 'New question' })
        ])
      }),
      expect.any(Object)
    );
  });
});
