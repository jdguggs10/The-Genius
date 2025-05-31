// web-app/src/components/ChatErrorBoundary.test.tsx
import { render, screen } from '@testing-library/react';
import ChatErrorBoundary from './ChatErrorBoundary';
import React from 'react';

const ProblemChild = () => {
  throw new Error('Test error from ProblemChild');
};

describe('ChatErrorBoundary', () => {
  // Suppress console.error output during this test
  let consoleErrorSpy: vi.SpyInstance;
  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });
  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  it('catches errors and renders fallback UI', () => {
    render(
      <ChatErrorBoundary>
        <ProblemChild />
      </ChatErrorBoundary>
    );
    expect(screen.getByText('Oops! Something went wrong.')).toBeInTheDocument();
    expect(screen.getByText('Refresh Page')).toBeInTheDocument();
    // Check if error details are present (optional, but good for coverage)
    const detailsElement = screen.getByText('Error Details').closest('details');
    expect(detailsElement).toBeInTheDocument();
    // You could click the summary to open details and check for error message content
  });

  it('renders children when there is no error', () => {
    render(
      <ChatErrorBoundary>
        <div>No Error Child</div>
      </ChatErrorBoundary>
    );
    expect(screen.getByText('No Error Child')).toBeInTheDocument();
  });
});
