// web-app/src/components/Chat.tsx
import { useState, useRef, useEffect } from 'react';
import { useDailyQuota } from '../hooks/useDailyQuota';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import QuotaModal from './QuotaModal.tsx';
import Message from './message';
import type { MessageType } from '../types';
import { shouldEnableWebSearch, getActualInput } from '../utils/webSearch'; // Import utilities

export default function Chat() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { count, increment, isLimitReached } = useDailyQuota();
  const [showQuotaModal, setShowQuotaModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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
    
    try {
      console.log('Sending request to backend...');
      console.log('Web search enabled:', enableWebSearch);
      
      // TODO: Use environment variable for backend URL
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'https://genius-backend-nhl3.onrender.com/advice';
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          conversation: [userMessage],
          enable_web_search: enableWebSearch
        })
      });
      
      console.log('Response received:', response);
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
    
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error response:', errorText);
        throw new Error(`Backend returned ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('Parsed response data:', data);
      
      if (!data.reply) {
        console.error('Response missing reply field:', data);
        throw new Error('Invalid response format from backend');
      }
      
      increment(); // Increment the quota count
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.reply 
      }]);
      
    } catch (error: unknown) {
      console.error('Detailed error:', error);
      
      // More specific error messages
      if (error instanceof Error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: 'Network error: Unable to connect to the AI service. Please check your internet connection and try again.' 
          }]);
        } else {
          setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: `Connection error: ${error.message}. Please try again.` 
          }]);
        }
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'An unexpected error occurred. Please try again.' 
        }]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Main container: Full height, flex column
  return (
    <div className="flex flex-col h-full max-h-screen">
      {/* 1. Header/Title Area */}
      <header className="p-4 border-b border-gray-200 bg-white">
        <h1 className="text-lg font-semibold text-gray-800">Fantasy AI Assistant</h1>
      </header>

      {/* 2. Message Display Area (Scrollable) */}
      <div className="flex-grow overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 && !isLoading ? ( // Show placeholder only if no messages and not loading
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            {/* Optional: <SomeIcon className="w-12 h-12 mb-4 text-gray-300" /> */}
            <h2 className="text-xl font-medium mb-2">Fantasy AI Assistant</h2>
            <p className="text-sm mb-1">Ask me anything about fantasy sports!</p>
            <div className="text-xs text-gray-400 text-center">
              <p>E.g., "Should I start Patrick Mahomes or Josh Allen?"</p>
              <p>Prefix with "search:" for live data: "search: who do the Yankees play today?"</p>
              <p className="mt-1">
                Or use keywords like "today", "current", "stats" for web search.
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <Message key={index} message={msg} />
          ))
        )}
        {isLoading && (
          <div className="flex items-center justify-center text-gray-500 p-4"> {/* Centered loading */}
            {/* Consider a more structured loading message, like a special bubble */}
            <div className="animate-pulse">AI is thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} /> {/* For scrolling to bottom */}
      </div>

      {/* 3. Message Input Area (Fixed at Bottom) */}
      <div className="p-3 border-t border-gray-200 bg-white"> {/* Adjusted padding */}
        <div className="flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message... (prefix with 'search:' for live data)"
            disabled={isLimitReached || isLoading}
            // Modernized input field:
            className="flex-1 w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading || isLimitReached}
            // Modernized send button:
            className="ml-2 p-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg disabled:opacity-50 flex items-center justify-center"
          >
            <PaperAirplaneIcon className="h-5 w-5" /> {/* Icon size is okay, can be adjusted if needed */}
          </button>
        </div>
        {/* Quota Display - relocated and styled */}
        <div className="text-xs text-gray-400 text-center mt-2">
          {count} of {5} messages used today
        </div>
      </div>
      
      {showQuotaModal && (
        <QuotaModal onClose={() => setShowQuotaModal(false)} />
      )}
    </div>
  );
}