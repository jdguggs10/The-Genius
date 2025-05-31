import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import ChatErrorBoundary from './components/ChatErrorBoundary.tsx';
// @ts-ignore: react-hot-toast has no type declarations
import { Toaster } from 'react-hot-toast';

// Suppress React DevTools message in development if needed
if (import.meta.env.DEV) {
  const originalLog = console.log;
  console.log = (...args) => {
    if (typeof args[0] === 'string' && args[0].includes('Download the React DevTools')) {
      return; // Suppress this specific message
    }
    originalLog.apply(console, args);
  };
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChatErrorBoundary>
      <App /> {/* App.tsx likely renders Chat.tsx */}
      <Toaster
        position="top-center"
        reverseOrder={false}
        toastOptions={{
          className: '', // General class for toasts
          duration: 5000,
          style: { // Default style
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            // theme: { // 'theme' is not a standard property here, use style or className
            //   primary: 'green',
            //   secondary: 'black',
            // },
          },
          error: {
            style: {
                background: '#fee2e2', // bg-red-100
                color: '#b91c1c', // text-red-700
            },
            iconTheme: {
                primary: '#ef4444', // text-red-500
                secondary: '#fee2e2', // bg-red-100
            }
          }
        }}
      />
    </ChatErrorBoundary>
  </React.StrictMode>,
)
