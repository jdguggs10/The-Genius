# DaisyUI Chat Implementation Guide for The Genius Web App

## 🎯 Why This Change Will Help

Your current chat implementation uses a lot of custom CSS classes to create chat bubbles. DaisyUI will:
- **Reduce your code** by ~50% (no more custom bubble styling)
- **Add professional arrow "tails"** to chat bubbles automatically
- **Improve consistency** with pre-tested designs
- **Keep all your features** (dark mode, animations, markdown, action buttons)

## 📋 Prerequisites Check

Good news! Your app already has everything needed:
- ✅ Tailwind CSS (already installed)
- ✅ TypeScript support
- ✅ Dark mode setup
- ✅ Framer Motion for animations

## 🚀 Step-by-Step Implementation

### Step 1: Install DaisyUI

Open your terminal in the `web-app` folder and run:

```bash
cd web-app
pnpm add -D daisyui
```

This installs DaisyUI as a development dependency.

### Step 2: Configure Tailwind

1. **Open** `web-app/tailwind.config.js` in your code editor
2. **Find** the `plugins: []` line (currently on line 17)
3. **Replace** it with:

```javascript
plugins: [require("daisyui")],
```

Your file should now look like this:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    { pattern: /^(bg|text|border|from|to)-/ },
    { pattern: /^dark:/ }
  ],
  theme: {
    extend: {},
  },
  darkMode: 'class',
  plugins: [require("daisyui")], // ← Added this line
}
```

### Step 3: Configure DaisyUI Themes

Still in `tailwind.config.js`, add DaisyUI configuration:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    { pattern: /^(bg|text|border|from|to)-/ },
    { pattern: /^dark:/ }
  ],
  theme: {
    extend: {},
  },
  darkMode: 'class',
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/theming/themes")["light"],
          // Customize to match your current colors
          "primary": "#3b82f6", // Your blue-500
          "primary-content": "#ffffff",
        },
        dark: {
          ...require("daisyui/src/theming/themes")["dark"],
          // Customize to match your current dark theme
          "base-100": "#262626", // neutral-800
          "base-200": "#171717", // neutral-900
          "primary": "#2563eb", // blue-600
          "primary-content": "#ffffff",
        }
      }
    ],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
  }
}
```

### Step 4: Create Enhanced Message Component

Create a new file `web-app/src/components/MessageDaisyUI.tsx`:

```tsx
// web-app/src/components/MessageDaisyUI.tsx
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion, useReducedMotion } from 'framer-motion';
import type { MessageType } from '../types';
import { ClipboardDocumentIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { UserIcon, SparklesIcon } from '@heroicons/react/24/solid';
// @ts-ignore: react-hot-toast has no type declarations
import toast from 'react-hot-toast';

type MessageProps = {
  message: MessageType;
};

export default function MessageDaisyUI({ message }: MessageProps) {
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
    setShowActions(false);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: shouldReduceMotion ? 0.1 : 0.3 }}
      className={`chat ${isUser ? 'chat-end' : 'chat-start'} relative group`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Action buttons - positioned absolutely */}
      {showActions && (
        <div
          className={`absolute z-10 flex items-center space-x-0.5 p-1 bg-base-200 rounded-md shadow-lg
                      ${isUser ? 'left-0 top-0' : 'right-0 top-0'}`}
        >
          <button
            onClick={handleCopy}
            title="Copy message"
            className="btn btn-ghost btn-xs"
          >
            <ClipboardDocumentIcon className="h-4 w-4" />
          </button>
          {isUser && (
            <>
              <button 
                title="Edit message (coming soon)" 
                disabled 
                className="btn btn-ghost btn-xs btn-disabled"
              >
                <PencilIcon className="h-4 w-4" />
              </button>
              <button 
                title="Delete message (coming soon)" 
                disabled 
                className="btn btn-ghost btn-xs btn-disabled"
              >
                <TrashIcon className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      )}

      {/* Avatar */}
      <div className="chat-image avatar">
        <div className="w-10 rounded-full">
          <div className={`w-full h-full rounded-full flex items-center justify-center ${
            isUser ? 'bg-primary text-primary-content' : 'bg-base-300'
          }`}>
            {isUser ? (
              <UserIcon className="h-5 w-5" />
            ) : (
              <SparklesIcon className="h-5 w-5" />
            )}
          </div>
        </div>
      </div>

      {/* Message bubble */}
      <div 
        className={`chat-bubble ${isUser ? 'chat-bubble-primary' : ''} max-w-[85%]`}
        aria-label={ariaLabel}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {/* Structured Advice Display */}
        {!isUser && message.structuredAdvice && (
          <div className="mt-3 pt-3 border-t border-base-content/20">
            {message.structuredAdvice.reasoning && (
              <div className="text-sm opacity-80">
                <span className="font-semibold">Reasoning:</span>
                <p className="mt-1">{message.structuredAdvice.reasoning}</p>
              </div>
            )}
            {message.structuredAdvice.model_identifier && (
              <div className="text-xs opacity-60 mt-2">
                Generated by {message.structuredAdvice.model_identifier}
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
```

### Step 5: Update Row Component in Chat

1. **Open** `web-app/src/components/chat.tsx`
2. **Find** the `Row` component (around line 26)
3. **Replace** the import at the top:

```tsx
// Replace this line:
import Message from './message';

// With this:
import MessageDaisyUI from './MessageDaisyUI';
```

4. **Update** the Row component:

```tsx
const Row = ({ index, style, data }: { index: number; style: React.CSSProperties; data: MessageType[] }) => {
  const message = data[index];
  if (!message) return null;

  if (message.role === 'assistant' && message.content === PLACEHOLDER_AI_MESSAGE) {
    return (
      <div style={style}>
        <SkeletonMessage key={message.id} />
      </div>
    );
  }
  return (
    <div style={style}>
      <MessageDaisyUI key={message.id} message={message} />
    </div>
  );
};
```

### Step 6: Update SkeletonMessage Component

1. **Open** `web-app/src/components/SkeletonMessage.tsx`
2. **Replace** the entire content with:

```tsx
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
```

### Step 7: Adjust Row Height

Since DaisyUI chat bubbles might have different heights:

1. **Open** `web-app/src/components/chat.tsx`
2. **Find** `const ITEM_SIZE = 90;` (around line 21)
3. **Change** it to:

```tsx
const ITEM_SIZE = 100; // Increased for DaisyUI chat components
```

### Step 8: Update CSS for DaisyUI

1. **Open** `web-app/src/index.css`
2. **Add** these styles at the end:

```css
/* DaisyUI Chat Customizations */
.chat-bubble {
  @apply shadow-sm max-w-[85%];
}

.chat-bubble-primary {
  @apply bg-primary text-primary-content;
}

/* Ensure proper markdown styling in chat bubbles */
.chat-bubble .prose {
  @apply text-inherit;
}

.chat-bubble .prose p {
  @apply my-1;
}

/* Dark mode adjustments */
.dark .chat-start .chat-bubble {
  @apply bg-neutral-700 text-neutral-100 border-neutral-600;
}
```

### Step 9: Test Your Changes

1. **Save all files**
2. **Restart your development server**:

```bash
# Press Ctrl+C to stop the current server
pnpm run dev
```

3. **Open** your browser to `http://localhost:5173`
4. **Test** the following:
   - Send a message - you should see the new chat bubbles with arrow tails
   - Check dark mode toggle still works
   - Hover over messages to see action buttons
   - Try copying a message
   - Check that AI responses with markdown still render correctly

## 🎨 Optional Customizations

### Custom Bubble Colors

In `MessageDaisyUI.tsx`, you can add custom classes:

```tsx
// For different AI response types
<div className={`chat-bubble ${
  message.structuredAdvice?.confidence_score > 0.8 
    ? 'bg-success text-success-content' 
    : ''
}`}>
```

### Timestamps

Add timestamps easily:

```tsx
<div className="chat-footer opacity-50">
  <time className="text-xs">{new Date(message.timestamp).toLocaleTimeString()}</time>
</div>
```

### Status Indicators

Add "delivered" or "read" indicators:

```tsx
<div className="chat-footer">
  <span>Delivered</span>
</div>
```

## 🐛 Troubleshooting

### If styles don't appear:
1. Make sure you saved `tailwind.config.js`
2. Restart the development server
3. Clear your browser cache (Ctrl+Shift+R)

### If dark mode looks wrong:
1. Check that `daisyui.themes` in `tailwind.config.js` includes both light and dark themes
2. Verify `darkMode: 'class'` is still in the config

### If animations are jumpy:
1. The `motion.div` wrapper should be on the outermost element
2. Don't animate width changes on chat bubbles

## ✅ Benefits You'll See

After implementing:
- **Cleaner code**: ~40% less CSS classes to maintain
- **Professional look**: Arrow tails point to the speaker
- **Consistency**: DaisyUI handles responsive sizing
- **Future-proof**: Easy to add timestamps, read receipts, typing indicators

## 🚀 Next Steps

Once this is working, you could:
1. Add typing indicators using `chat-footer`
2. Implement message grouping (multiple messages from same sender)
3. Add image/file attachment support
4. Create custom themes for different sports (blue for football, green for baseball, etc.)

## 📚 Resources

- DaisyUI Chat Documentation: https://daisyui.com/components/chat/
- DaisyUI Themes: https://daisyui.com/docs/themes/
- Your current Message component (for reference): `web-app/src/components/message.tsx`
