// web-app/src/components/SkeletonMessage.test.tsx
import { render, screen } from '@testing-library/react';
import SkeletonMessage from './SkeletonMessage';
import React from 'react';
import { useReducedMotion } from 'framer-motion';

// Mock framer-motion specifically for useReducedMotion
vi.mock('framer-motion', async (importOriginal) => {
    const original = await importOriginal() as any; // Use 'any' or a more specific type if available
    return {
        ...original,
        useReducedMotion: vi.fn(), // Mock useReducedMotion
    };
});

describe('SkeletonMessage', () => {
  beforeEach(() => {
    // Reset mock implementation before each test
    (useReducedMotion as vi.Mock).mockReturnValue(false);
  });

  it('renders without crashing for AI message', () => {
    render(<SkeletonMessage isUser={false} />);
    expect(screen.getByLabelText('AI message loading')).toBeInTheDocument();
  });

  it('renders without crashing for User message', () => {
    render(<SkeletonMessage isUser={true} />);
    expect(screen.getByLabelText('User message loading')).toBeInTheDocument();
  });

  it('has animate-pulse class when reduced motion is false', () => {
    (useReducedMotion as vi.Mock).mockReturnValue(false);
    const { container } = render(<SkeletonMessage />);
    // motion.li is the root, check its class
    expect(container.firstChild).toHaveClass('animate-pulse');
  });

  it('does not have animate-pulse class when reduced motion is true', () => {
    (useReducedMotion as vi.Mock).mockReturnValue(true);
    const { container } = render(<SkeletonMessage />);
    // motion.li is the root, check its class
    expect(container.firstChild).not.toHaveClass('animate-pulse');
  });

  // Clean up mocks after all tests in this file
  afterAll(() => {
    vi.unmock('framer-motion');
  });
});
