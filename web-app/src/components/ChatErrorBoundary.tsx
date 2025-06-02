// web-app/src/components/ChatErrorBoundary.tsx
import React, { Component } from 'react';
import type { ReactNode } from 'react';
import { logger } from '../utils/logger';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ChatErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logger.error("Uncaught error in Chat component:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      const isDevelopment = import.meta.env.DEV;
      
      return (
        <div className="flex flex-col items-center justify-center h-screen bg-red-50 p-4">
          <div className="bg-white p-8 rounded-lg shadow-xl text-center max-w-md">
            <h1 className="text-2xl font-bold text-red-600 mb-4">Oops! Something went wrong.</h1>
            <p className="text-gray-700 mb-4">
              We encountered an unexpected problem. Please try refreshing the page or contact support if the issue persists.
            </p>
            {isDevelopment && this.state.error && (
              <details className="mt-4 text-left bg-gray-100 p-3 rounded">
                <summary className="text-sm text-gray-600 cursor-pointer">Error Details (Development)</summary>
                <pre className="mt-2 text-xs text-red-500 whitespace-pre-wrap">
                  {this.state.error.toString()}
                  {this.state.error.stack && `
${this.state.error.stack}`}
                </pre>
              </details>
            )}
            <button
              onClick={() => window.location.reload()}
              className="mt-6 bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded transition-colors"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ChatErrorBoundary;
