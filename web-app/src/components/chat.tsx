// web-app/src/components/Chat.tsx
import { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, MagnifyingGlassIcon } from '@heroicons/react/24/solid';
import MessageDaisyUI from './MessageDaisyUI';
import SkeletonMessage from './SkeletonMessage';
// AnimatePresence removed as it's unlikely to work well with react-window item recycling without significant effort
import type { MessageType, AdviceRequest } from '../types';
import { useConversationManager } from '../hooks/useConversationManager';
import { useSSEClient } from '../hooks/useSSEClient';
import { useScrollAnchor } from '../hooks/useScrollAnchor';
// @ts-ignore: react-window has no type declarations
import { FixedSizeList } from 'react-window';
// @ts-ignore: react-hot-toast has no type declarations
import toast from 'react-hot-toast';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline'; // Using outline for theme toggle
import { useTheme } from '../hooks/useTheme';
import { logger } from '../utils/logger';
import { getAdviceUrl, logApiConfig, getDefaultModelSettingUrl } from '../utils/api';

const PLACEHOLDER_AI_MESSAGE = "_PLACEHOLDER_AI_MESSAGE_";
const ITEM_SIZE = 100; // Increased for DaisyUI chat components

// Define Row component for FixedSizeList
// It's defined outside Chat or wrapped in useCallback if inside and accessing Chat's props/state.
// For simplicity and stability with react-window, define outside or ensure useCallback has minimal dependencies.
const Row = ({ index, style, data }: { index: number; style: React.CSSProperties; data: MessageType[] }) => {
  const message = data[index];
  if (!message) return null;

  if (message.role === 'assistant' && message.content === PLACEHOLDER_AI_MESSAGE) {
    return (
      <li style={style} role="listitem" className="snap-start">
        <SkeletonMessage key={message.id} />
      </li>
    );
  }
  return (
    <li style={style} role="listitem" className="snap-start">
      <MessageDaisyUI key={message.id} message={message} />
    </li>
  );
};


export default function Chat() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [streamingText, setStreamingText] = useState(''); // Kept for compatibility with useEffect, but actual streaming text is now currentAIMessageText
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [defaultModelNameFromAPI, setDefaultModelNameFromAPI] = useState<string>('Default Model'); // Initialize with a fallback
  const inputRef = useRef<HTMLInputElement>(null);
  const currentAssistantMessageIdRef = useRef<string | null>(null);
  const [currentAIMessageText, setCurrentAIMessageText] = useState('');
  const listRef = useRef<FixedSizeList>(null);
  const listContainerRef = useRef<HTMLDivElement>(null);
  const [listHeight, setListHeight] = useState(0);

  const { theme, setTheme } = useTheme();

  // SSE client setup - now using centralized API config
  const adviceUrl = getAdviceUrl();
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

  // Log API configuration on mount for debugging
  useEffect(() => {
    logApiConfig();

    // Fetch default model name from API
    const fetchModelName = async () => {
      try {
        const response = await fetch(getDefaultModelSettingUrl());
        if (!response.ok) {
          // Silently handle 404 - endpoint doesn't exist yet
          if (response.status === 404) {
            logger.debug('Default model endpoint not available yet, using fallback');
            return;
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data && data.model) {
          setDefaultModelNameFromAPI(data.model);
        } else {
          logger.debug('No model name in API response, using fallback');
        }
      } catch (error) {
        // Only log actual errors, not expected 404s
        if (error instanceof Error && !error.message.includes('404')) {
          logger.error('Error fetching default model name:', error);
        }
      }
    };

    fetchModelName();
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
  }, [messages.length]);

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
    
    logger.info('Input:', input);
    logger.info('Web search always enabled');
    logger.info('Last response ID:', lastResponseId);
    
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

    logger.info('Streaming request payload via SSE:', {
      conversationLength: conversationForAPI.length,
      previousResponseId: requestPayload.previous_response_id,
      enableWebSearch: requestPayload.enable_web_search
    });

    streamSSEResponse(adviceUrl, requestPayload, {
      onEvent: (eventData) => {
        logger.debug('🎯 Received SSE event:', eventData.type, eventData.data);
        const assistantMessageId = currentAssistantMessageIdRef.current;
        if (!assistantMessageId && !(eventData.type === 'error' || (eventData.type === 'status_update' && !eventData.data.response_id))) {
          logger.warn("No current assistant message ID for targeted message:", eventData);
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
            logger.info('Unhandled SSE event type from server:', eventData.type, eventData.data);
        }
      },
      onError: (error) => {
        logger.error('SSE streaming error:', error);
        const assistantMessageId = currentAssistantMessageIdRef.current;
        setStatusMessage(null);
        setIsSearching(false);
        setIsLoading(false);
        
        // Handle timeout errors with user-friendly messages
        let userFriendlyMessage: string;
        let toastDuration = 5000;
        
        if (error.name === 'TimeoutError') {
          if (error.message.includes('Connection timeout')) {
            userFriendlyMessage = 'Connection timed out. The server may be busy. Please try again.';
            toastDuration = 6000; // Longer duration for timeout messages
          } else if (error.message.includes('Stream timeout')) {
            userFriendlyMessage = 'Request timed out. The AI took too long to respond. Please try again.';
            toastDuration = 6000;
          } else {
            userFriendlyMessage = 'Request timed out. Please try again.';
            toastDuration = 6000;
          }
        } else {
          userFriendlyMessage = error.message || 'An unknown error occurred';
        }
        
        toast.error(`AI Error: ${userFriendlyMessage}`, { 
          id: `ai-err-${assistantMessageId || 'general'}`,
          duration: toastDuration
        });
        
        if (assistantMessageId) {
          updateMessage(assistantMessageId, { content: `Error: ${userFriendlyMessage}` });
          currentAssistantMessageIdRef.current = null;
        }
      },
      onComplete: () => {
        // no-op; completion handled in 'response_complete'
      },
      // Timeout configuration - adjust based on expected response times
      connectionTimeoutMs: 45000,  // 45 seconds for initial connection (web search can take time)
      streamTimeoutMs: 180000      // 3 minutes for stream inactivity (AI generation can be slow)
    });
  };

  // Main container: Full height, flex column with custom background - Centered layout
  return (
    <div className="flex flex-col h-full max-h-screen bg-app-bg dark:bg-app-bg-dark chat-container">
      {/* Theme toggle button - positioned absolutely in top right */}
      <div className="absolute top-4 right-4 z-20">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          className="p-2 rounded-full hover:bg-white/20 dark:hover:bg-black/20 text-app-text-muted dark:text-app-text-muted-dark transition-colors backdrop-blur-sm font-button focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
        >
          {(theme === 'dark' || (theme === 'system' && typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches)) ? (
            <SunIcon className="h-5 w-5" />
          ) : (
            <MoonIcon className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Main content area - Messages or Welcome */}
      {messages.length > 0 || isLoading ? (
        <>
          {/* Header when there are messages */}
          <header className="p-4 bg-surface-card-light/90 dark:bg-surface-card-dark/90 backdrop-blur-sm chat-header">
            <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between sm:space-y-0 space-y-2 chat-header-content">
              <div className="flex items-center space-x-2">
                <img 
                  src="/favicon-32.png" 
                  alt="The Genius Logo" 
                  className="w-6 h-6 sm:w-8 sm:h-8"
                />
                <h1 className="text-lg sm:text-xl lg:text-2xl font-headline font-bold text-app-text dark:text-app-text-dark chat-title">The Genius</h1>
                {isSearching && (
                  <div className="flex items-center space-x-1 text-primary-600 dark:text-primary-400 chat-search-indicator">
                    <MagnifyingGlassIcon className="h-3 w-3 sm:h-4 sm:w-4 animate-spin" />
                    <span className="text-xs sm:text-sm">Searching...</span>
                  </div>
                )}
              </div>
              {lastResponseId && (
                <div className="text-xs text-app-text-muted dark:text-app-text-muted-dark">
                  Conversation Active
                </div>
              )}
            </div>
          </header>

          {/* Message Display Area */}
          <div ref={listContainerRef} className="flex-grow overflow-hidden p-2 sm:p-4 scroll-smooth message-list-container">
            <div className="max-w-4xl mx-auto h-full">
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
                  overscanCount={12}
                  innerElementType="ul"
                  outerElementType={(props: React.HTMLProps<HTMLDivElement>) => (
                    <div 
                      {...props}
                      role="log"
                      aria-live="polite"
                      aria-relevant="additions"
                      aria-label="Chat conversation messages"
                      className="scroll-smooth snap-y snap-end overflow-y-auto"
                    />
                  )}
                >
                  {Row}
                </FixedSizeList>
              )}
            </div>
          </div>

          {/* Input Area for active conversations */}
          <div className="p-2 sm:p-4 bg-surface-card-light/95 dark:bg-surface-card-dark/95 backdrop-blur-sm shadow-lg">
            <div className="flex justify-center items-center composer-input-area">
              <div className="flex items-center space-x-2 composer-input-wrapper">
                <div className="relative">
                  <input
                    ref={inputRef}
                    id="chat-input"
                    name="chat-input"
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Type here for Fantasy Advice..."
                    disabled={isLoading}
                    aria-label="Chat input for fantasy sports advice"
                    className="pl-16 pr-20 py-4 bg-surface-input-light dark:bg-surface-input-light border border-surface-border-light dark:border-surface-border-light text-app-text dark:text-app-text placeholder-app-text-muted rounded-full focus:outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 focus:ring-2 focus:ring-primary-400/50 focus:border-primary-400 transition-all text-base composer-input"
                    style={{
                      paddingLeft: '4rem',
                      paddingRight: '5rem',
                      borderRadius: '9999px',
                      width: '384px',
                      height: '48px'
                    }}
                  />
                </div>
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  aria-label={isLoading ? 'Sending message...' : 'Send message'}
                  className="p-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white rounded-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all transform hover:scale-105 active:scale-95 shadow-lg font-button font-bold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 composer-send-button"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <PaperAirplaneIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
              
            {/* Hidden status for screen readers */}
            <div id="chat-status" role="status" className="sr-only">
              {isLoading && 'Sending message...'}
              {isSearching && 'Searching for information...'}
              {statusMessage && statusMessage}
            </div>
          </div>
        </>
      ) : (
        /* Welcome/Landing View - Centered Layout */
        <div className="flex-grow flex flex-col items-center justify-center p-4 sm:p-8">
          <div className="mx-auto text-center">
            {/* Main Title with Logo - Larger and Centered */}
            <div className="flex items-center justify-center mb-8 sm:mb-12">
              <img 
                src="/apple-touch-icon.png" 
                alt="The Genius Logo" 
                className="w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 mr-4 sm:mr-6 welcome-logo"
              />
              <div className="text-[6rem] sm:text-[7rem] lg:text-[8rem] xl:text-[9rem] font-headline font-bold text-app-text dark:text-app-text-dark welcome-title">
                The Genius
              </div>
            </div>
            
            {/* Welcome Input Card */}
            <div className="mb-8 sm:mb-12 flex justify-center welcome-input-card">
              <div className="bg-surface-card-light dark:bg-surface-card-dark rounded-xl shadow-lg p-1 sm:p-2">
                <div className="flex items-center space-x-3 composer-input-area">
                  <div className="relative composer-input-wrapper">
                    <input
                      ref={inputRef}
                      id="chat-input"
                      name="chat-input"
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                      placeholder="Type here for Fantasy Advice..."
                      disabled={isLoading}
                      aria-label="Chat input for fantasy sports advice"
                      className="pl-16 pr-20 py-4 bg-surface-input-light dark:bg-surface-input-light border border-surface-border-light dark:border-surface-border-light text-app-text dark:text-app-text placeholder-app-text-muted rounded-full focus:outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 focus:ring-2 focus:ring-primary-400/50 focus:border-primary-400 transition-all text-base composer-input"
                      style={{
                        paddingLeft: '4rem',
                        paddingRight: '5rem',
                        borderRadius: '9999px',
                        width: '384px',
                        height: '48px'
                      }}
                    />
                  </div>
                  <button
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                    aria-label={isLoading ? 'Sending message...' : 'Send message'}
                    className="p-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white rounded-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all transform hover:scale-105 active:scale-95 shadow-lg font-button font-bold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500 composer-send-button"
                  >
                    {isLoading ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <PaperAirplaneIcon className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Status/Model Info */}
            <div className="mt-8 text-sm text-app-text-muted dark:text-app-text-muted-dark composer-status">
              Powered by {defaultModelNameFromAPI}
            </div>
          </div>
        </div>
      )}

      {/* New Messages Chip */}
      {showNewMessagesChip && (
        <button
          onClick={() => scrollToBottom('smooth', messages.length)}
          aria-label="Scroll to new messages"
          className="fixed bottom-20 right-4 sm:right-10 z-10 bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-full shadow-lg transition-opacity duration-300 animate-bounce dark:bg-primary-600 dark:hover:bg-primary-700 font-button focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
        >
          ↓ New messages
        </button>
      )}
    </div>
  );
}