// web-app/src/components/chat.test.tsx
import { render, screen, cleanup } from '@testing-library/react';
import Chat from './chat'; // Adjust path as necessary
import { vi } from 'vitest';

// Mock the useDailyQuota hook
vi.mock('../hooks/useDailyQuota', () => ({
  useDailyQuota: () => ({
    count: 0,
    increment: vi.fn(),
    isLimitReached: false,
  }),
}));

// Mock environment variables if your component uses them directly
// For VITE_BACKEND_URL
vi.stubGlobal('importMeta', {
  env: {
    VITE_BACKEND_URL: 'http://localhost:3000/api',
  },
});


describe('Chat Component', () => {
  afterEach(() => {
    cleanup(); // Clean up the DOM after each test
  });

  it('renders the initial model name in the "Powered by" text', () => {
    render(<Chat />);
    
    // The text "Powered by GPT-4o with real-time web search" is expected.
    // This text is within a <span> which has 'hidden sm:inline' classes.
    // getByText should find it if it's in the DOM, even if styled as hidden.
    // We use a regex for case-insensitivity and to match the full relevant string.
    const poweredByText = screen.getByText(/Powered by GPT-4o with real-time web search/i);

    expect(poweredByText).toBeInTheDocument();
  });
});
