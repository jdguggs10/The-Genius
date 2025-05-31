// web-app/src/components/SkeletonMessage.tsx
import { motion, useReducedMotion } from 'framer-motion';

const SkeletonMessage = ({ isUser = false }: { isUser?: boolean }) => {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      layout
      initial={{ opacity: shouldReduceMotion ? 1 : 0, y: shouldReduceMotion ? 0 : 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: shouldReduceMotion ? 0.05 : 0.3 }}
      className={`chat ${isUser ? 'chat-end' : 'chat-start'} ${shouldReduceMotion ? '' : 'animate-pulse'}`}
      aria-label={isUser ? "User message loading" : "AI message loading"}
    >
      {/* Avatar skeleton */}
      <div className="chat-image avatar">
        <div className="w-10 rounded-full bg-base-300"></div>
      </div>

      {/* Message skeleton */}
      <div className="chat-bubble">
        <div className="space-y-2">
          <div className="h-3 bg-base-content/20 rounded w-32 sm:w-48"></div>
          <div className="h-3 bg-base-content/20 rounded w-24 sm:w-40"></div>
          <div className="h-3 bg-base-content/20 rounded w-36 sm:w-56"></div>
        </div>
      </div>
    </motion.div>
  );
};

export default SkeletonMessage;
