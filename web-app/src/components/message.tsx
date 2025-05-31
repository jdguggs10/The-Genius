// web-app/src/components/Message.tsx
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, useReducedMotion } from 'framer-motion';
import type { MessageType } from '../types';
import { ClipboardDocumentIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { UserIcon, SparklesIcon } from '@heroicons/react/24/solid'; // Using solid variants
import toast from 'react-hot-toast';

type MessageProps = {
  message: MessageType;
};

export default function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';
  const ariaLabel = `${isUser ? 'User said' : 'AI replied'}: ${message.content.substring(0, 50)}${message.content.length > 50 ? '...' : ''}`;
  const [showActions, setShowActions] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      toast.success('Copied to clipboard!', { duration: 1500, id: `copy-${message.id}` });
    } catch (err) {
      console.error('Failed to copy message: ', err);
      toast.error('Failed to copy.', { duration: 1500, id: `copy-err-${message.id}` });
    }
    setShowActions(false); // Hide actions after click
  };

  return (
    <motion.li
      layout // Keep layout for smooth positioning
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 10 }} // Reduce or remove vertical motion
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }} // Simple fade out is usually fine
      transition={{ duration: shouldReduceMotion ? 0.1 : 0.3 }} // Faster transition if reduced
      aria-label={ariaLabel}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 relative group`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Actions Bar - positioned absolutely relative to this motion.li */}
      {showActions && (
        <div
            className={`absolute z-10 flex items-center space-x-0.5 p-1 bg-gray-100 dark:bg-neutral-800 rounded-md shadow-lg
                        ${isUser ? 'left-0 top-[-12px]' : 'right-0 top-[-12px]'}`}
                        // Adjust 'left-0' or 'right-0' based on actual bubble position if needed
                        // top-[-12px] attempts to place it slightly above the bubble area
        >
          <button
            onClick={handleCopy}
            title="Copy message"
            className="p-1 hover:bg-gray-200 dark:hover:bg-neutral-700 rounded text-gray-600 dark:text-gray-300"
          >
            <ClipboardDocumentIcon className="h-4 w-4" />
          </button>
          {isUser && (
            <>
              <button title="Edit message (coming soon)" disabled className="p-1 text-gray-400 dark:text-neutral-500 cursor-not-allowed">
                <PencilIcon className="h-4 w-4" />
              </button>
              <button title="Delete message (coming soon)" disabled className="p-1 text-gray-400 dark:text-neutral-500 cursor-not-allowed">
                <TrashIcon className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      )}

      {/* Original message structure (avatar + bubble) */}
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3 max-w-[85%]`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-blue-600 text-white dark:bg-blue-500 ml-3' : 'bg-gray-200 text-gray-700 dark:bg-neutral-600 dark:text-neutral-300 mr-3'
        }`}>
          {isUser ? (
            <UserIcon className="h-5 w-5" />
          ) : (
            <SparklesIcon className="h-5 w-5" />
          )}
        </div>

        {/* Message Content */}
        <div className={`rounded-2xl shadow-sm ${
          isUser
            ? 'bg-blue-600 text-white dark:bg-blue-500'
            : 'bg-white text-gray-800 border border-gray-200 dark:bg-neutral-700 dark:text-neutral-100 dark:border-neutral-600'
        }`}>
          {/* Main Message */}
          <div className="px-4 py-3">
            {isUser ? (
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            ) : (
              <div className="prose prose-sm max-w-none text-gray-800 dark:text-neutral-200 [&_p]:my-1 [&_p]:text-gray-800 dark:[&_p]:text-neutral-200">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
          </div>

          {/* Structured Advice Display */}
          {!isUser && message.structuredAdvice && (
            <div className="border-t border-gray-100 dark:border-neutral-600/50 bg-gray-50/50 dark:bg-neutral-600/30 rounded-b-2xl">
              {/* Confidence Score - Hidden for now */}
              {/* {message.structuredAdvice.confidence_score && (
                <div className="px-4 py-2 border-b border-gray-100 dark:border-neutral-600">
                  <div className="flex items-center space-x-2">
                    <ChartBarIcon className="h-4 w-4 text-blue-500" />
                    <span className="text-xs font-medium text-gray-600 dark:text-neutral-300">Confidence:</span>
                    <div className="flex items-center space-x-2 flex-1">
                      <div className="bg-gray-200 rounded-full h-2 flex-1 max-w-[100px]">
                        <div 
                          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${message.structuredAdvice.confidence_score * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 min-w-[2rem]">
                        {Math.round(message.structuredAdvice.confidence_score * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              )} */}

              {/* Reasoning */}
              {message.structuredAdvice.reasoning && (
                <div className="px-4 py-2 border-b border-gray-100 dark:border-neutral-600">
                  <div className="flex items-start space-x-2">
                    <span className="text-xs font-medium text-gray-600 dark:text-neutral-300">Reasoning:</span>
                    <p className="text-xs text-gray-700 dark:text-neutral-200 mt-1 leading-relaxed">
                      {message.structuredAdvice.reasoning}
                    </p>
                  </div>
                </div>
              )}

              {/* Alternatives - Hidden for now */}
              {/* {message.structuredAdvice.alternatives && message.structuredAdvice.alternatives.length > 0 && (
                <div className="px-4 py-2">
                  <div className="flex items-start space-x-2">
                    <ArrowRightIcon className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <span className="text-xs font-medium text-gray-600 dark:text-neutral-300">Alternatives:</span>
                      <div className="mt-1 space-y-1">
                        {message.structuredAdvice.alternatives.map((alt, index) => (
                          <div key={index} className="text-xs">
                            <span className="font-medium text-gray-700 dark:text-neutral-200">{alt.player}</span>
                            {alt.reason && (
                              <span className="text-gray-600 dark:text-neutral-300 ml-1">- {alt.reason}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )} */}

              {/* Model Identifier */}
              {message.structuredAdvice.model_identifier && (
                <div className="px-4 py-1 text-xs text-gray-400 dark:text-neutral-500 text-center">
                  Generated by {message.structuredAdvice.model_identifier}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.li>
  );
}