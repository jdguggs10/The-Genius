// web-app/src/components/Message.tsx
import ReactMarkdown from 'react-markdown';

type MessageProps = {
  message: {
    role: 'user' | 'assistant';
    content: string;
  };
};

export default function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`my-2 ${isUser ? 'text-right' : ''}`}>
      <div
        className={`inline-block max-w-[80%] p-3 rounded-lg ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-none'
            : 'bg-gray-100 text-gray-800 rounded-bl-none'
        }`}
      >
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}