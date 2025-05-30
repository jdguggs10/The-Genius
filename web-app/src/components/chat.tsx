// web-app/src/components/Chat.tsx
import { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, MagnifyingGlassIcon } from '@heroicons/react/24/solid';
import Message from './message';
import type { MessageType, AdviceRequest } from '../types';
import { shouldEnableWebSearch, getActualInput, getSearchHint } from '../utils/webSearch'; // Import utilities
import { useConversationManager } from '../hooks/useConversationManager';
import { useSSEClient } from '../hooks/useSSEClient';

export default function Chat() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [modelName, setModelName] = useState<string>(''); // State for dynamic model name pulled from backend
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use the conversation manager
  const {
    messages,
    lastResponseId,
    addMessage,
    updateMessage,
    setLastResponseId,
    getConversationForAPI
  } = useConversationManager();

  // Use the improved SSE client
  const { streamSSEResponse } = useSSEClient();

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

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingText, statusMessage]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const enableWebSearch = shouldEnableWebSearch(input);
    const actualInput = getActualInput(input);
    
    console.log('Input:', input);
    console.log('Web search enabled:', enableWebSearch);
    console.log('Actual input to send:', actualInput);
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
    setStreamingText('');
    setStatusMessage(null);
    
    // Create assistant placeholder
    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantPlaceholder: MessageType = { 
      role: 'assistant', 
      content: '',
      id: assistantMessageId
    };
    addMessage(assistantPlaceholder);
    
    // Prepare request payload
    const conversationForAPI = getConversationForAPI();
    conversationForAPI.push(userMessage); // Include the new user message
    
    const requestPayload: AdviceRequest = {
      conversation: conversationForAPI,
      enable_web_search: enableWebSearch,
      previous_response_id: lastResponseId || undefined
    };

    console.log('Sending request payload:', {
      conversationLength: conversationForAPI.length,
      previousResponseId: requestPayload.previous_response_id,
      enableWebSearch: requestPayload.enable_web_search
    });
    
    let accumulatedText = '';
    let currentResponseId: string | null = null;
    
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'https://genius-backend-nhl3.onrender.com/advice';
      
      await streamSSEResponse(backendUrl, requestPayload, {
        onEvent: (event) => {
          console.log('Received SSE event:', event.type, event.data);
          
          switch (event.type) {
            case 'status_update':
              if (event.data.response_id) {
                currentResponseId = event.data.response_id;
              }
              
              setStatusMessage(event.data.message || 'Processing...');
              setStreamingText('');
              
              updateMessage(assistantMessageId, {
                content: event.data.message || 'Processing...'
              });
              
              if (event.data.status === 'web_search_searching' || event.data.status === 'web_search_started') {
                setIsSearching(true);
              } else {
                setIsSearching(false);
              }
              break;
              
            case 'text_delta':
              setStatusMessage(null);
              setIsSearching(false);
              accumulatedText += event.data.delta;
              setStreamingText(accumulatedText);
              
              updateMessage(assistantMessageId, {
                content: accumulatedText
              });
              break;
              
            case 'response_complete':
              setStatusMessage(null);
              setIsSearching(false);
              setStreamingText('');
              
              const structuredAdvice = event.data.final_json;
              if (event.data.response_id) {
                currentResponseId = event.data.response_id;
              }
              
              if (structuredAdvice?.model_identifier) {
                setModelName(structuredAdvice.model_identifier);
              }
              
              updateMessage(assistantMessageId, {
                content: structuredAdvice?.main_advice || accumulatedText,
                structuredAdvice: structuredAdvice || undefined,
                responseId: currentResponseId || undefined
              });
              
              // Update the last response ID for future conversations
              if (currentResponseId) {
                setLastResponseId(currentResponseId);
                console.log('Updated last response ID:', currentResponseId);
              }
              break;
              
            case 'error':
              setStatusMessage(null);
              setIsSearching(false);
              const errorMessage = event.data.message || 'An API error occurred';
              
              updateMessage(assistantMessageId, {
                content: `Error: ${errorMessage}`
              });
              break;
              
            default:
              console.log('Unhandled SSE event type:', event.type, event.data);
          }
        },
        
        onError: (error) => {
          console.error('SSE streaming error:', error);
          let errorMessage = 'An unexpected error occurred. Please try again.';
          
          if (error.message.includes('Backend returned') || error.message.includes('API error')) {
            errorMessage = error.message;
          } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorMessage = 'Network error: Unable to connect to the AI service. Please check your internet connection and try again.';
          } else {
            errorMessage = `Connection error: ${error.message}. Please try again.`;
          }
          
          updateMessage(assistantMessageId, {
            content: errorMessage
          });
        },
        
        onComplete: () => {
          console.log('SSE stream completed');
        }
      });
      
    } catch (error) {
      console.error('Request failed:', error);
      updateMessage(assistantMessageId, {
        content: 'Failed to send request. Please try again.'
      });
    } finally {
      setIsLoading(false);
      setIsSearching(false);
      setStreamingText('');
      setStatusMessage(null);
    }
  };

  // Main container: Full height, flex column
  return (
    <div className="flex flex-col h-full max-h-screen bg-gradient-to-br from-stone-100 to-stone-200">
      {/* Enhanced Header */}
      <header className="p-4 border-b border-gray-200 bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="flex flex-col sm:flex-row items-center justify-between sm:space-y-0 space-y-2">
          <div className="flex items-center space-x-2">
            <h1 className="text-base sm:text-lg font-semibold text-gray-800">The Genius</h1>
            {isSearching && (
              <div className="flex items-center space-x-1 text-blue-600">
                <MagnifyingGlassIcon className="h-3 w-3 sm:h-4 sm:w-4 animate-spin" />
                <span className="text-xs sm:text-sm">Searching...</span>
              </div>
            )}
          </div>
          {lastResponseId && (
            <div className="text-xs text-gray-400">
              Conversation Active
            </div>
          )}
        </div>
      </header>

      {/* Message Display Area (Scrollable) */}
      <div className="flex-grow overflow-y-auto p-2 sm:p-4 space-y-4">
        {messages.length === 0 && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="bg-white rounded-2xl p-4 sm:p-8 shadow-lg border border-gray-100 w-full max-w-md mx-auto">
              <h2 className="text-lg sm:text-xl font-medium mb-1 sm:mb-2 text-center text-gray-800">The Genius</h2>
              <p className="text-xs sm:text-sm mb-2 sm:mb-4 text-center">Get AI-powered fantasy sports advice!</p>
              <div className="text-xs text-gray-400 space-y-1 sm:space-y-2">
                <p className="bg-gray-50 rounded p-1.5 sm:p-2">
                  <strong>Example:</strong> "Should I start Patrick Mahomes or Josh Allen?"
                </p>
                <p className="bg-blue-50 rounded p-1.5 sm:p-2">
                  <strong>Live Data:</strong> Prefix with "search:" or use keywords like "today", "current", "stats"
                </p>
                <p className="bg-green-50 rounded p-1.5 sm:p-2">
                  <strong>Real-time:</strong> Get streaming responses with detailed analysis
                </p>
                <p className="bg-purple-50 rounded p-1.5 sm:p-2">
                  <strong>Context:</strong> Follow-up questions remember previous conversation
                </p>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, index) => (
              <Message key={msg.id || index} message={msg} />
            ))}
            
            {/* Streaming/Status indicator - simplified and combined */}
            {isLoading && (streamingText || statusMessage) && (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                  <span className="text-gray-600 text-xs font-medium">AI</span>
                </div>
                <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100 max-w-3xl">
                  <div className="text-gray-800">
                    {statusMessage ? statusMessage : streamingText}
                    {!statusMessage && streamingText && <span className="inline-block w-2 h-4 bg-blue-500 ml-1 animate-pulse"></span>}
                  </div>
                </div>
              </div>
            )}
            
            {/* Basic loading indicator when no text or status yet */}
            {isLoading && !streamingText && !statusMessage && (
              <div className="flex items-center justify-center text-gray-500 p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  <span className="ml-2">AI is thinking...</span>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Enhanced Input Area */}
      <div className="p-2 sm:p-4 border-t border-gray-200 bg-white/80 backdrop-blur-sm">
        <div className="flex items-center space-x-2 sm:space-x-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about fantasy sports..."
              disabled={isLoading}
              className="w-full px-3 sm:px-4 py-2 sm:py-3 pr-10 sm:pr-12 border border-gray-300 rounded-lg sm:rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all disabled:bg-gray-100 disabled:cursor-not-allowed text-sm sm:text-base"
            />
            {shouldEnableWebSearch(input) && (
              <MagnifyingGlassIcon className="absolute right-2 sm:right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 text-blue-500" />
            )}
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-2 sm:p-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg sm:rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all transform hover:scale-105 active:scale-95 shadow-lg"
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
          <span className="text-gray-400">
            {input ? getSearchHint(input) : `Powered by ${modelName} with conversation memory ${lastResponseId ? '(Active)' : '(New)'}`}
          </span>
        </div>
      </div>
    </div>
  );
}