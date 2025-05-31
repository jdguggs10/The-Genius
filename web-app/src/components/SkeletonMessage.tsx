// web-app/src/components/SkeletonMessage.tsx
import { motion, useReducedMotion } from 'framer-motion';

const SkeletonMessage = ({ isUser = false }: { isUser?: boolean }) => {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.li
      layout
      initial={{ opacity: shouldReduceMotion ? 1 : 0, y: shouldReduceMotion ? 0 : 10 }} // Start opaque and no y-shift if reduced, else fade in with y-shift
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: shouldReduceMotion ? 0.05 : 0.3 }} // Quicker fade if reduced
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 ${shouldReduceMotion ? '' : 'animate-pulse'}`}
      aria-label={isUser ? "User message loading" : "AI message loading"}
    >
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3 max-w-[85%]`}>
        {/* Avatar Skeleton */}
        <div className={`w-8 h-8 rounded-full flex-shrink-0 ${
          isUser ? 'bg-gray-300 dark:bg-neutral-700 ml-3' : 'bg-gray-200 dark:bg-neutral-600 mr-3'
        }`}></div>

        {/* Message Content Skeleton */}
        <div className={`rounded-2xl p-3 shadow-sm ${
          isUser ? 'bg-gray-300 dark:bg-neutral-700' : 'bg-gray-200 dark:bg-neutral-600'
        }`}>
          <div className="space-y-2">
            <div className="h-3 bg-gray-400 dark:bg-neutral-500 rounded w-32 sm:w-48"></div>
            <div className="h-3 bg-gray-400 dark:bg-neutral-500 rounded w-24 sm:w-40"></div>
            <div className="h-3 bg-gray-400 dark:bg-neutral-500 rounded w-36 sm:w-56"></div>
          </div>
        </div>
      </div>
    </motion.li>
  );
};

export default SkeletonMessage;
