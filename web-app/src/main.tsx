import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import ChatErrorBoundary from './components/ChatErrorBoundary';
// @ts-ignore: react-hot-toast has no type declarations
import { Toaster } from 'react-hot-toast';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChatErrorBoundary>
      <App />
      <Toaster
        position="top-center"
        reverseOrder={false}
        toastOptions={{
          className: '',
          duration: 5000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
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
