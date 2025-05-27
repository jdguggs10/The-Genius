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
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] px-4 py-2.5 rounded-xl shadow-sm ${ // Increased max-width slightly, adjusted padding
          isUser
            ? 'bg-sky-600 text-white'
            : 'bg-white text-gray-800 border border-gray-200' // Solid border for assistant
        }`}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p> // User message as plain text, respects newlines
        ) : (
          // For assistant messages, ensure the prose styles don't override base text color too aggressively
          // or clash with the bubble. Tailwind Prose usually tries to adapt.
          <div className="prose prose-sm max-w-none [&_p]:my-0"> {/* Targeting prose p margin specifically if needed */}
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}