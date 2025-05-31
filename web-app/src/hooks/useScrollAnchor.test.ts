// web-app/src/hooks/useScrollAnchor.test.ts
import { renderHook, act } from '@testing-library/react';
import { useScrollAnchor } from './useScrollAnchor';
import React from 'react';

// Mock FixedSizeList ref for testing scrollToItem
const mockScrollToItem = vi.fn();
const mockListRef = {
  current: {
    scrollToItem: mockScrollToItem,
  } as any, // Cast to any to simplify mock
};

// Mock HTMLElement for scrollableContainerRef
const mockScrollableContainer = {
    scrollHeight: 2000,
    scrollTop: 0,
    clientHeight: 500,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    scrollTo: vi.fn(),
    firstChild: { // Mock potential inner div for scrollHeight calculation
        scrollHeight: 2000,
    }
} as unknown as HTMLElement;


describe('useScrollAnchor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset parts of mockScrollableContainer that might be changed in tests
    mockScrollableContainer.scrollTop = 0;
  });

  it('should initialize correctly', () => {
    const { result } = renderHook(() => useScrollAnchor(mockListRef, 10));
    expect(result.current.isAtBottom).toBe(true);
    expect(result.current.showNewMessagesChip).toBe(false);
  });

  it('scrollToBottom should call listRef.scrollToItem if listRef is provided', () => {
    const { result } = renderHook(() => useScrollAnchor(mockListRef, 10));
    act(() => {
      result.current.scrollToBottom('smooth', 10);
    });
    expect(mockScrollToItem).toHaveBeenCalledWith(9, 'smooth');
    expect(result.current.isAtBottom).toBe(true);
    expect(result.current.showNewMessagesChip).toBe(false);
  });

  it('handleScroll updates isAtBottom', () => {
    const { result } = renderHook(() => useScrollAnchor(mockListRef, 20));
    // Assign a mock scrollable container to the ref for testing handleScroll
    (result.current.scrollableContainerRef as React.MutableRefObject<HTMLElement | null>).current = mockScrollableContainer;

    // Simulate scrolling to middle
    act(() => {
        mockScrollableContainer.scrollTop = 500; // Not at bottom
        // Simulate FixedSizeList onScroll event object structure
        result.current.handleScroll({ scrollOffset: 500, scrollUpdateWasRequested: false } as any);
    });
    expect(result.current.isAtBottom).toBe(false);

    // Simulate scrolling to bottom
    act(() => {
        mockScrollableContainer.scrollTop = 1500; // At bottom (2000 - 1500 - 500 = 0)
        result.current.handleScroll({ scrollOffset: 1500, scrollUpdateWasRequested: false } as any);
    });
    expect(result.current.isAtBottom).toBe(true);
    expect(result.current.showNewMessagesChip).toBe(false); // Should hide chip when scrolled to bottom
  });

  it('handleScroll works with standard scroll events if listRef not present in hook call', () => {
    const { result } = renderHook(() => useScrollAnchor(undefined, 20)); // No listRef
    (result.current.scrollableContainerRef as React.MutableRefObject<HTMLElement | null>).current = mockScrollableContainer;

    act(() => {
        mockScrollableContainer.scrollTop = 500;
        result.current.handleScroll({ currentTarget: mockScrollableContainer } as unknown as Event);
    });
    expect(result.current.isAtBottom).toBe(false);

    act(() => {
        mockScrollableContainer.scrollTop = 1500;
        result.current.handleScroll({ currentTarget: mockScrollableContainer } as unknown as Event);
    });
    expect(result.current.isAtBottom).toBe(true);
  });
});
