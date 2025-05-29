// web-app/src/components/Chat.tsx
import { useState, useRef, useEffect } from 'react';
import { useDailyQuota } from '../hooks/useDailyQuota';
import { PaperAirplaneIcon, MagnifyingGlassIcon } from '@heroicons/react/24/solid';
import QuotaModal from './QuotaModal.tsx';
import Message from './message';
import type { MessageType } from '../types';
import { shouldEnableWebSearch, getActualInput, getSearchHint } from '../utils/webSearch'; // Import utilities

export default function Chat() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const { count, increment, isLimitReached } = useDailyQuota();
  const [showQuotaModal, setShowQuotaModal] = useState(false);
  const [modelName, setModelName] = useState<string>(''); // State for dynamic model name pulled from backend
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
  }, [messages, streamingText]);

  // Check if quota reached
  useEffect(() => {
    if (isLimitReached) {
      setShowQuotaModal(true);
    }
  }, [isLimitReached]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || isLimitReached) return;
    
    const enableWebSearch = shouldEnableWebSearch(input);
    const actualInput = getActualInput(input);
    
    // Add debug logging for web search detection
    console.log('Input:', input);
    console.log('Web search enabled:', enableWebSearch);
    console.log('Actual input to send:', actualInput);
    
    const userMessage = { role: 'user', content: actualInput } as MessageType;
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setIsSearching(false);
    setStreamingText('');
    
    // Add placeholder assistant message for streaming
    const assistantMessageId = Date.now().toString();
    const assistantPlaceholder = { 
      role: 'assistant', 
      content: '',
      id: assistantMessageId 
    } as MessageType;
    setMessages(prev => [...prev, assistantPlaceholder]);
    
    let accumulatedText = '';
    let structuredAdvice: MessageType['structuredAdvice'] | null = null;
    
    try {
      console.log('Sending SSE request to backend...');
      
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'https://genius-backend-nhl3.onrender.com/advice';
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache'
        },
        body: JSON.stringify({ 
          conversation: [userMessage],
          enable_web_search: enableWebSearch
        })
      });
      
      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }
      
      if (!response.body) {
        throw new Error('No response body received');
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('event: ')) {
              continue;
            }
            
            if (line.startsWith('data: ')) {
              try {
                const eventData = JSON.parse(line.slice(6));
                
                if (eventData.status === 'searching') {
                  // Handle web search status
                  setIsSearching(true);
                  setStreamingText('🔍 Searching the web for current information...');
                } else if (eventData.delta) {
                  // Handle text deltas
                  setIsSearching(false);
                  accumulatedText += eventData.delta;
                  setStreamingText(accumulatedText);
                  
                  // Update the assistant message with accumulated text
                  setMessages(prev => 
                    prev.map(msg => 
                      msg.id === assistantMessageId 
                        ? { ...msg, content: accumulatedText }
                        : msg
                    )
                  );
                } else if (eventData.status === 'complete' && eventData.final_json) {
                  // Handle final structured advice
                  structuredAdvice = eventData.final_json;
                  setIsSearching(false);
                  setStreamingText('');
                  
                  // Update model name if backend sent a model identifier
                  if (structuredAdvice?.model_identifier) {
                    setModelName(structuredAdvice.model_identifier);
                  }

                  // Update message with structured advice main content
                  setMessages(prev => 
                    prev.map(msg => 
                      msg.id === assistantMessageId 
                        ? { 
                            ...msg, 
                            content: structuredAdvice?.main_advice || accumulatedText,
                            structuredAdvice: structuredAdvice || undefined
                          }
                        : msg
                    )
                  );
                } else if (eventData.error) {
                  throw new Error(`API Error: ${eventData.message}`);
                }
              } catch (parseError) {
                console.warn('Failed to parse event data:', parseError);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
      
      increment(); // Increment the quota count
      
    } catch (error: unknown) {
      console.error('Streaming error:', error);
      
      let errorMessage = 'An unexpected error occurred. Please try again.';
      if (error instanceof Error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          errorMessage = 'Network error: Unable to connect to the AI service. Please check your internet connection and try again.';
        } else {
          errorMessage = `Connection error: ${error.message}. Please try again.`;
        }
      }
      
      // Update the assistant message with error
      setMessages(prev => 
        prev.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, content: errorMessage }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
      setIsSearching(false);
      setStreamingText('');
    }
  };

  // Main container: Full height, flex column
  return (
    <div className="flex flex-col h-full max-h-screen bg-gradient-to-br from-stone-100 to-stone-200">
      {/* Enhanced Header */}
      <header className="p-4 border-b border-gray-200 bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="flex flex-col sm:flex-row items-center justify-between sm:space-y-0 space-y-2">
          <div className="flex items-center space-x-2">
            <img src="/apple-touch-icon.png" alt="Logo" className="h-6 w-6 sm:h-8 sm:w-8 rounded-md" />
            <h1 className="text-base sm:text-lg font-semibold text-gray-800">The Genius</h1>
            {isSearching && (
              <div className="flex items-center space-x-1 text-blue-600">
                <MagnifyingGlassIcon className="h-3 w-3 sm:h-4 sm:w-4 animate-spin" />
                <span className="text-xs sm:text-sm">Searching...</span>
              </div>
            )}
          </div>
          <div className="text-xs text-gray-500">
            {count} of {5} messages used today
          </div>
        </div>
      </header>

      {/* Message Display Area (Scrollable) */}
      <div className="flex-grow overflow-y-auto p-2 sm:p-4 space-y-4">
        {messages.length === 0 && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="bg-white rounded-2xl p-4 sm:p-8 shadow-lg border border-gray-100 w-full max-w-md mx-auto">
              {/* Logo removed from here as it's already in the header */}
              <h2 className="text-lg sm:text-xl font-medium mb-1 sm:mb-2 text-center text-gray-800 mt-4">The Genius</h2>
              <p className="text-xs sm:text-sm mb-2 sm:mb-4 text-center">Get AI-powered fantasy sports advice!</p>
              <div className="text-xs text-gray-400 space-y-1 sm:space-y-2">
                <p className="bg-gray-50 rounded p-1.5 sm:p-2">
                  💡 <strong>Example:</strong> "Should I start Patrick Mahomes or Josh Allen?"
                </p>
                <p className="bg-blue-50 rounded p-1.5 sm:p-2">
                  🔍 <strong>Live Data:</strong> Prefix with "search:" or use keywords like "today", "current", "stats"
                </p>
                <p className="bg-green-50 rounded p-1.5 sm:p-2">
                  ⚡ <strong>Real-time:</strong> Get streaming responses with detailed analysis
                </p>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, index) => (
              <Message key={index} message={msg} />
            ))}
            
            {/* Streaming indicator */}
            {isLoading && streamingText && (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                </div>
                <div className="bg-white rounded-lg p-3 shadow-sm border border-gray-100 max-w-3xl">
                  <div className="text-gray-800">
                    {streamingText}
                    <span className="inline-block w-2 h-4 bg-blue-500 ml-1 animate-pulse"></span>
                  </div>
                </div>
              </div>
            )}
            
            {/* Basic loading indicator when no text yet */}
            {isLoading && !streamingText && (
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
              placeholder={isLimitReached ? "Daily limit reached" : "Ask about fantasy sports..."}
              disabled={isLimitReached || isLoading}
              className="w-full px-3 sm:px-4 py-2 sm:py-3 pr-10 sm:pr-12 border border-gray-300 rounded-lg sm:rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all disabled:bg-gray-100 disabled:cursor-not-allowed text-sm sm:text-base"
            />
            {shouldEnableWebSearch(input) && (
              <MagnifyingGlassIcon className="absolute right-2 sm:right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 text-blue-500" />
            )}
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading || isLimitReached}
            className="p-2 sm:p-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg sm:rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all transform hover:scale-105 active:scale-95 shadow-lg"
          >
            {isLoading ? (
              <div className="w-4 h-4 sm:w-5 sm:w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <PaperAirplaneIcon className="h-4 w-4 sm:h-5 sm:w-5" />
            )}
          </button>
        </div>
        
        {/* Enhanced Quota Display */}
        <div className="flex flex-col sm:flex-row items-center justify-between mt-1.5 sm:mt-2 text-xs">
          <div className="text-gray-400 text-center sm:text-left mb-1 sm:mb-0">
            {isLimitReached ? (
              <span className="text-red-500 font-medium">Daily limit reached</span>
            ) : (
              <span className="hidden sm:inline">{input ? getSearchHint(input) : `Powered by ${modelName} with real-time web search`}</span>
            )}
          </div>
          <div className="flex items-center space-x-1">
            <div className="flex space-x-1">
              {Array.from({length: 5}).map((_, i) => (
                <div 
                  key={i}
                  className={`w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full ${i < count ? 'bg-blue-500' : 'bg-gray-200'}`}
                />
              ))}
            </div>
            <span className="text-gray-500 ml-1 sm:ml-2">{count}/5</span>
          </div>
        </div>
      </div>
      
      {showQuotaModal && (
        <QuotaModal onClose={() => setShowQuotaModal(false)} />
      )}
    </div>
  );
}