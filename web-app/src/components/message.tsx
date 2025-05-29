// web-app/src/components/Message.tsx
import ReactMarkdown from 'react-markdown';
import { ChartBarIcon, LightBulbIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import type { MessageType } from '../types';

type MessageProps = {
  message: MessageType;
};

export default function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3 max-w-[85%]`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-blue-600 ml-3' : 'bg-gray-100 mr-3'
        }`}>
          {isUser ? (
            <span className="text-white text-sm font-medium">You</span>
          ) : (
            <span className="text-gray-600 text-xs font-medium">AI</span>
          )}
        </div>

        {/* Message Content */}
        <div className={`rounded-2xl shadow-sm ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-white text-gray-800 border border-gray-200'
        }`}>
          {/* Main Message */}
          <div className="px-4 py-3">
            {isUser ? (
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            ) : (
              <div className="prose prose-sm max-w-none text-gray-800 [&_p]:my-1 [&_p]:text-gray-800">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
          </div>

          {/* Structured Advice Display */}
          {!isUser && message.structuredAdvice && (
            <div className="border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
              {/* Confidence Score - Hidden for now */}
              {/* {message.structuredAdvice.confidence_score && (
                <div className="px-4 py-2 border-b border-gray-100">
                  <div className="flex items-center space-x-2">
                    <ChartBarIcon className="h-4 w-4 text-blue-500" />
                    <span className="text-xs font-medium text-gray-600">Confidence:</span>
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
                <div className="px-4 py-2 border-b border-gray-100">
                  <div className="flex items-start space-x-2">
                    <LightBulbIcon className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <span className="text-xs font-medium text-gray-600">Reasoning:</span>
                      <p className="text-xs text-gray-700 mt-1 leading-relaxed">
                        {message.structuredAdvice.reasoning}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Alternatives - Hidden for now */}
              {/* {message.structuredAdvice.alternatives && message.structuredAdvice.alternatives.length > 0 && (
                <div className="px-4 py-2">
                  <div className="flex items-start space-x-2">
                    <ArrowRightIcon className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <span className="text-xs font-medium text-gray-600">Alternatives:</span>
                      <div className="mt-1 space-y-1">
                        {message.structuredAdvice.alternatives.map((alt, index) => (
                          <div key={index} className="text-xs">
                            <span className="font-medium text-gray-700">{alt.player}</span>
                            {alt.reason && (
                              <span className="text-gray-600 ml-1">- {alt.reason}</span>
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
                <div className="px-4 py-1 text-xs text-gray-400 text-center">
                  Generated by {message.structuredAdvice.model_identifier}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}