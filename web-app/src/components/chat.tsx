// web-app/src/components/Chat.tsx
import { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, MagnifyingGlassIcon } from '@heroicons/react/24/solid';
import Message from './message';
import SkeletonMessage from './SkeletonMessage';
// AnimatePresence removed as it's unlikely to work well with react-window item recycling without significant effort
import type { MessageType, AdviceRequest } from '../types';
import { useConversationManager } from '../hooks/useConversationManager';
// useSSEClient imported instead of useChatSocket
import { useSSEClient } from '../hooks/useSSEClient';
import { useScrollAnchor } from '../hooks/useScrollAnchor';
// @ts-ignore: react-window has no type declarations
import { FixedSizeList } from 'react-window';
// @ts-ignore: react-hot-toast has no type declarations
import toast from 'react-hot-toast';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline'; // Using outline for theme toggle
import { useTheme } from '../hooks/useTheme';

const PLACEHOLDER_AI_MESSAGE = "_PLACEHOLDER_AI_MESSAGE_";
const ITEM_SIZE = 90; // Approximate height in pixels for a message row - NEEDS TUNING

// Define Row component for FixedSizeList
// It's defined outside Chat or wrapped in useCallback if inside and accessing Chat's props/state.
// For simplicity and stability with react-window, define outside or ensure useCallback has minimal dependencies.
const Row = ({ index, style, data }: { index: number; style: React.CSSProperties; data: MessageType[] }) => {
  const message = data[index];
  if (!message) return null;

  if (message.role === 'assistant' && message.content === PLACEHOLDER_AI_MESSAGE) {
    return (
      <div style={style}>
        <SkeletonMessage key={message.id} />
      </div>
    );
  }
  return (
    <div style={style}>
      <Message key={message.id} message={message} />
    </div>
  );
};


export default function Chat() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [streamingText, setStreamingText] = useState(''); // Kept for compatibility with useEffect, but actual streaming text is now currentAIMessageText
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [modelName, setModelName] = useState<string>('');
  const inputRef = useRef<HTMLInputElement>(null);
  const currentAssistantMessageIdRef = useRef<string | null>(null);
  const [currentAIMessageText, setCurrentAIMessageText] = useState('');
  const listRef = useRef<FixedSizeList>(null);
  const listContainerRef = useRef<HTMLDivElement>(null);
  const [listHeight, setListHeight] = useState(0);

  const { theme, setTheme } = useTheme();

  // SSE client setup
  const apiBase = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  const adviceUrl = `${apiBase.replace(/\/$/, '')}/advice`;
  const { streamSSEResponse } = useSSEClient();
  
  // Use the conversation manager
  const {
    messages,
    lastResponseId,
    addMessage,
    updateMessage,
    setLastResponseId,
    getConversationForAPI
  } = useConversationManager();

  // Scroll anchor hook, now that messages is defined
  // eslint-disable-next-line no-use-before-define
  const {
    scrollableContainerRef,
    isAtBottom,
    showNewMessagesChip,
    setShowNewMessagesChip,
    scrollToBottom,
    handleScroll // This will be passed to FixedSizeList's onScroll
  } = useScrollAnchor(listRef, messages.length);

  // Fetch default model from backend on mount
  useEffect(() => {
    const fetchDefaultModel = async () => {
      try {
        const url = new URL(import.meta.env.VITE_BACKEND_URL ?? 'https://genius-backend-nhl3.onrender.com/advice');
        url.pathname = '/model';
        const response = await fetch(url.toString());
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        if (data.model) {
          setModelName(data.model);
        }
      } catch (error) {
        console.error('Failed to fetch default model:', error);
        setModelName('GPT-4.1');
      }
    };
    fetchDefaultModel();
  }, []);

  // Updated scroll logic using useScrollAnchor
  useEffect(() => {
    if (listContainerRef.current) {
      const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
          setListHeight(entry.contentRect.height);
        }
      });
      resizeObserver.observe(listContainerRef.current);
      setListHeight(listContainerRef.current.clientHeight); // Initial height
      return () => resizeObserver.disconnect();
    }
  }, []);

  // Updated scroll logic using useScrollAnchor
  useEffect(() => {
    if (messages.length > 0 || streamingText || statusMessage) {
      const lastMessage = messages[messages.length - 1];
      const isLastMessageFromUser = lastMessage?.role === 'user';

      if (isLastMessageFromUser) {
        scrollToBottom('auto', messages.length);
      } else if (isAtBottom) {
        scrollToBottom('smooth', messages.length);
      } else {
        const lastMessageIsUseful = messages.length > 0 &&
                                    messages[messages.length -1].role === 'assistant' &&
                                    !messages[messages.length -1].content.startsWith('Error:') &&
                                    !messages[messages.length -1].content.startsWith('Processing...');
        if (streamingText || lastMessageIsUseful) {
          setShowNewMessagesChip(true);
        }
      }
    }
  // Ensure all dependencies that might affect scrolling or message count are included.
  }, [messages, streamingText, statusMessage, isAtBottom, scrollToBottom, setShowNewMessagesChip, messages.length]); // streamingText and statusMessage still used here from old logic

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const enableWebSearch = true;
    const actualInput = input;
    
    console.log('Input:', input);
    console.log('Web search always enabled');
    console.log('Last response ID:', lastResponseId);
    
    // Create user message
    const userMessage: MessageType = { 
      role: 'user', 
      content: actualInput,
      id: Date.now().toString()
    };
    
    // Add user message to conversation
    addMessage(userMessage);
    setInput('');
    setIsLoading(true);
    setIsSearching(false);
    setCurrentAIMessageText('');
    setStatusMessage(null);
    
    // Create assistant placeholder
    const assistantMessageId = `assistant-${Date.now()}`;
    currentAssistantMessageIdRef.current = assistantMessageId;
    const assistantPlaceholder: MessageType = { 
      role: 'assistant', 
      content: PLACEHOLDER_AI_MESSAGE,
      id: assistantMessageId
    };
    addMessage(assistantPlaceholder);
    
    // Prepare request payload
    const conversationForAPI = getConversationForAPI();
    conversationForAPI.push(userMessage);
    
    const requestPayload: AdviceRequest = {
      conversation: conversationForAPI,
      enable_web_search: enableWebSearch,
      previous_response_id: lastResponseId || undefined
    };

    console.log('Streaming request payload via SSE:', {
      conversationLength: conversationForAPI.length,
      previousResponseId: requestPayload.previous_response_id,
      enableWebSearch: requestPayload.enable_web_search
    });

    streamSSEResponse(adviceUrl, requestPayload, {
      onEvent: (eventData) => {
        const assistantMessageId = currentAssistantMessageIdRef.current;
        if (!assistantMessageId && !(eventData.type === 'error' || (eventData.type === 'status_update' && !eventData.data.response_id))) {
          console.warn("No current assistant message ID for targeted message:", eventData);
          return;
        }
        switch (eventData.type) {
          case 'status_update':
            const statusMsgContent = eventData.data.message || 'Processing...';
            if (assistantMessageId && eventData.data.response_id) {
              updateMessage(assistantMessageId, { content: statusMsgContent });
            } else if (!eventData.data.response_id) {
              setStatusMessage(statusMsgContent);
            }
            setCurrentAIMessageText('');
            setStreamingText('');
            setIsSearching(eventData.data.status === 'web_search_searching' || eventData.data.status === 'web_search_started');
            break;
          case 'text_delta':
            if (!assistantMessageId) break;
            setStatusMessage(null);
            setIsSearching(false);
            const newText = currentAIMessageText + (eventData.data.delta || '');
            setCurrentAIMessageText(newText);
            updateMessage(assistantMessageId, { content: newText });
            setStreamingText(newText);
            break;
          case 'response_complete':
            if (!assistantMessageId) break;
            setStatusMessage(null);
            setIsSearching(false);
            setIsLoading(false);
            const structuredAdvice = eventData.data.final_json;
            if (structuredAdvice?.model_identifier) setModelName(structuredAdvice.model_identifier);
            updateMessage(assistantMessageId, {
              content: structuredAdvice?.main_advice || currentAIMessageText || "Response complete.",
              structuredAdvice: structuredAdvice || undefined,
              responseId: eventData.data.response_id || undefined
            });
            if (eventData.data.response_id) setLastResponseId(eventData.data.response_id);
            setCurrentAIMessageText('');
            setStreamingText('');
            currentAssistantMessageIdRef.current = null;
            break;
          case 'error':
            setStatusMessage(null);
            setIsSearching(false);
            setIsLoading(false);
            const errorMsg = eventData.data.message || 'An unknown server error occurred';
            toast.error(`AI Error: ${errorMsg}`, { id: `ai-err-${assistantMessageId || 'general'}` });
            const errorContent = `Error: ${errorMsg}`;
            if (assistantMessageId) updateMessage(assistantMessageId, { content: errorContent });
            else setStatusMessage(errorContent);
            setCurrentAIMessageText('');
            setStreamingText('');
            if (assistantMessageId) currentAssistantMessageIdRef.current = null;
            break;
          default:
            console.log('Unhandled SSE event type from server:', eventData.type, eventData.data);
        }
      },
      onError: (error) => {
        console.error('SSE streaming error:', error);
        const assistantMessageId = currentAssistantMessageIdRef.current;
        setStatusMessage(null);
        setIsSearching(false);
        setIsLoading(false);
        const errorMsg = error.message || 'An unknown error occurred';
        toast.error(`AI Error: ${errorMsg}`, { id: `ai-err-${assistantMessageId || 'general'}` });
        if (assistantMessageId) {
          updateMessage(assistantMessageId, { content: `Error: ${errorMsg}` });
          currentAssistantMessageIdRef.current = null;
        }
      },
      onComplete: () => {
        // no-op; completion handled in 'response_complete'
      }
    });
  };

  // Main container: Full height, flex column
  return (
    <div className="flex flex-col h-full max-h-screen bg-gradient-to-br from-stone-100 to-stone-200 dark:from-neutral-800 dark:to-neutral-900">
      {/* Enhanced Header */}
      <header className="p-4 border-b border-gray-200 dark:border-neutral-700 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-sm shadow-sm">
        <div className="flex flex-col sm:flex-row items-center justify-between sm:space-y-0 space-y-2">
          <div className="flex items-center space-x-2">
            <h1 className="text-base sm:text-lg font-semibold text-gray-800 dark:text-neutral-200">The Genius</h1>
            {isSearching && (
              <div className="flex items-center space-x-1 text-blue-600 dark:text-blue-400">
                <MagnifyingGlassIcon className="h-3 w-3 sm:h-4 sm:w-4 animate-spin" />
                <span className="text-xs sm:text-sm">Searching...</span>
              </div>
            )}
          </div>
          {lastResponseId && (
            <div className="text-xs text-gray-400 dark:text-neutral-500">
              Conversation Active
            </div>
          )}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
              className="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-neutral-700 text-gray-600 dark:text-gray-300 transition-colors"
            >
              {/* This logic correctly shows the icon for the *next* theme state upon click,
                  or rather, shows the icon opposite to the current *displayed* theme.
                  If current theme is dark (or system is dark), show SunIcon to switch to light.
                  If current theme is light (or system is light), show MoonIcon to switch to dark.
              */}
              {(theme === 'dark' || (theme === 'system' && typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches)) ? (
                <SunIcon className="h-5 w-5" />
              ) : (
                <MoonIcon className="h-5 w-5" />
              )}
            </button>
            {/* Optional: System theme button can be added here if desired */}
          </div>
        </div>
      </header>

      {/* Message Display Area (Scrollable) */}
      <div ref={listContainerRef} className="flex-grow overflow-hidden p-2 sm:p-4"> {/* Parent for FixedSizeList, needs defined height */}
        {listHeight > 0 && messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-neutral-400">
                <div className="bg-white dark:bg-neutral-800 rounded-2xl p-4 sm:p-8 shadow-lg border border-gray-100 dark:border-neutral-700 w-full max-w-md mx-auto">
                    <h2 className="text-lg sm:text-xl font-medium mb-1 sm:mb-2 text-center text-gray-800 dark:text-neutral-200">The Genius</h2>
                    <p className="text-xs sm:text-sm mb-2 sm:mb-4 text-center dark:text-neutral-400">Get AI-powered fantasy sports advice!</p>
                    <div className="text-xs text-gray-400 dark:text-neutral-500 space-y-1 sm:space-y-2">
                        <p className="bg-gray-50 dark:bg-neutral-700/50 rounded p-1.5 sm:p-2"><strong>Example:</strong> "Should I start Patrick Mahomes or Josh Allen?"</p>
                        <p className="bg-blue-50 dark:bg-blue-900/30 rounded p-1.5 sm:p-2"><strong>Live Data:</strong> Prefix with "search:" or use keywords like "today", "current", "stats"</p>
                        <p className="bg-green-50 dark:bg-green-900/30 rounded p-1.5 sm:p-2"><strong>Real-time:</strong> Get streaming responses with detailed analysis</p>
                        <p className="bg-purple-50 dark:bg-purple-900/30 rounded p-1.5 sm:p-2"><strong>Context:</strong> Follow-up questions remember previous conversation</p>
                    </div>
                </div>
            </div>
        )}
        {listHeight > 0 && (messages.length > 0 || isLoading) && (
          <FixedSizeList
            height={listHeight}
            itemCount={messages.length}
            itemSize={ITEM_SIZE}
            itemData={messages}
            outerRef={scrollableContainerRef}
            ref={listRef}
            width="100%"
            onScroll={handleScroll}
            // className="space-y-4" // Removed: FixedSizeList positions items absolutely, spacing should be in ITEM_SIZE or Row style
          >
            {Row}
          </FixedSizeList>
        )}
        {/* messagesEndRef is removed as FixedSizeList handles scrolling */}
      </div>

      {/* New Messages Chip */}
      {showNewMessagesChip && (
        <button
          onClick={() => scrollToBottom('smooth', messages.length)}
          className="fixed bottom-20 right-4 sm:right-10 z-10 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg transition-opacity duration-300 animate-bounce dark:bg-blue-600 dark:hover:bg-blue-700"
        >
          ↓ New messages
        </button>
      )}

      {/* Enhanced Input Area */}
      <div className="p-2 sm:p-4 border-t border-gray-200 dark:border-neutral-700 bg-white/80 dark:bg-neutral-900/80 backdrop-blur-sm">
        <div className="flex items-center space-x-2 sm:space-x-3">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about fantasy sports..."
              disabled={isLoading}
              className="w-full px-3 sm:px-4 py-2 sm:py-3 pr-10 sm:pr-12 border border-gray-300 dark:bg-neutral-800 dark:border-neutral-600 dark:text-neutral-100 dark:placeholder-neutral-400 rounded-lg sm:rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all disabled:bg-gray-100 dark:disabled:bg-neutral-700 disabled:cursor-not-allowed text-sm sm:text-base"
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-2 sm:p-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg sm:rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all transform hover:scale-105 active:scale-95 shadow-lg dark:from-blue-600 dark:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800"
          >
            {isLoading ? (
              <div className="w-4 h-4 sm:w-5 sm:w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <PaperAirplaneIcon className="h-4 w-4 sm:h-5 sm:w-5" />
            )}
          </button>
        </div>
        
        {/* Enhanced Status Display */}
        <div className="mt-1.5 sm:mt-2 text-xs">
          <span className="text-gray-400 dark:text-neutral-500">
            Powered by {modelName} with conversation memory {lastResponseId ? '(Active)' : '(New)'}
          </span>
        </div>
      </div>
    </div>
  );
}