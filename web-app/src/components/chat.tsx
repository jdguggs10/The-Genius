// web-app/src/components/Chat.tsx
import { useState, useRef, useEffect } from 'react';
import { useDailyQuota } from '../hooks/useDailyQuota';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import QuotaModal from './QuotaModal.tsx';
import Message from './message';

type MessageType = {
  role: 'user' | 'assistant';
  content: string;
};

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
    
    const userMessage = { role: 'user', content: input } as MessageType;
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await fetch('https://genius-backend-nhl3.onrender.com/advice', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        mode: 'cors',
        body: JSON.stringify({ 
          conversation: [userMessage],
          enable_web_search: input.toLowerCase().includes('stats') || 
                            input.toLowerCase().includes('current') ||
                            input.toLowerCase().includes('latest')
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to get response');
      }
      
      // Debug: Let's see what we're actually getting
      console.log('Response status:', response.status);
      console.log('Response headers:', [...response.headers.entries()]);

      const responseText = await response.text();
      console.log('Raw response:', responseText);

      let data;
      try {
        data = JSON.parse(responseText);
      } catch (e) {
        console.error('Failed to parse JSON:', e);
        console.error('Response text was:', responseText);
        throw new Error(`Server returned non-JSON response: ${responseText}`);
      }
      
      increment(); // Increment the quota count
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.reply 
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again later.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-center mb-4">Fantasy AI Assistant</h1>
      
      <div className="flex-1 overflow-auto bg-white rounded-lg shadow p-4 mb-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 my-20">
            <p>Ask me anything about fantasy sports!</p>
            <p className="mt-2 text-sm">Examples:</p>
            <ul className="mt-1 text-sm">
              <li>"Should I start Patrick Mahomes or Josh Allen this week?"</li>
              <li>"Who are the top sleeper picks for fantasy baseball?"</li>
              <li>"Is Christian McCaffrey worth trading for?"</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, index) => (
            <Message key={index} message={msg} />
          ))
        )}
        {isLoading && (
          <div className="flex items-center text-gray-500 mt-2">
            <div className="animate-pulse">AI is thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="flex items-center">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
          disabled={isLimitReached || isLoading}
          className="flex-1 p-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading || isLimitReached}
          className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-r-lg disabled:opacity-50"
        >
          <PaperAirplaneIcon className="h-5 w-5" />
        </button>
      </div>
      
      <div className="text-center text-sm text-gray-500 mt-2">
        {count} of {5} messages used today
      </div>
      
      {showQuotaModal && (
        <QuotaModal onClose={() => setShowQuotaModal(false)} />
      )}
    </div>
  );
}