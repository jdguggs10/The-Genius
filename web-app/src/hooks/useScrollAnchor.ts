// web-app/src/hooks/useScrollAnchor.ts
import { useCallback, useEffect, useRef, useState } from 'react';
// @ts-ignore: react-window has no type declarations
import type { FixedSizeList } from 'react-window';

// Hook now needs the list instance ref and total item count for scrolling
export function useScrollAnchor(
  listRef?: React.RefObject<FixedSizeList | null>, // Optional: listRef for direct scroll control
  itemCount?: number // Optional: itemCount for scrolling to end
) {
  const scrollableContainerRef = useRef<HTMLElement | null>(null); // Can be Div or FixedSizeList's outerRef
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [showNewMessagesChip, setShowNewMessagesChip] = useState(false);

  const handleScroll = useCallback((event?: Event | { scrollOffset: number, scrollUpdateWasRequested: boolean }) => { // Event can be from direct scroll or FixedSizeList's onScroll
    let containerToUse: HTMLElement | null = null;

    if (event && 'scrollOffset' in event) { // This is FixedSizeList's onScroll event
        // For FixedSizeList, we need to use its internal scroll metrics if available,
        // or rely on scrollableContainerRef if it's correctly set to the scrollable element.
        // The event object from onScroll gives scrollOffset (scrollTop). We need scrollHeight and clientHeight.
        containerToUse = scrollableContainerRef.current; // outerRef should be this
    } else if (event && event.currentTarget instanceof HTMLElement) { // This is a standard scroll event
        containerToUse = event.currentTarget;
    } else { // Fallback or initial
        containerToUse = scrollableContainerRef.current;
    }

    if (containerToUse) {
      const threshold = 50;
      // For FixedSizeList, scrollHeight might be on an inner div, not the outerRef.
      // listRef.current?.props.itemSize * listRef.current?.props.itemCount can give total height.
      // However, FixedSizeList's onScroll provides scrollOffset, which is scrollTop.
      // We need a reliable way to get scrollHeight and clientHeight for the actual scrollable element.
      // Assuming scrollableContainerRef (outerRef) has these, or its first child (innerRef).

      let scrollTop = 0;
      let scrollHeight = containerToUse.scrollHeight;
      let clientHeight = containerToUse.clientHeight;

      if (event && 'scrollOffset' in event) {
          scrollTop = event.scrollOffset;
      } else {
          scrollTop = containerToUse.scrollTop;
      }

      // If scrollableContainerRef is the outer div of FixedSizeList, its first child is usually the one with the full scrollHeight.
      // Let's try to use that if it seems more accurate.
      if (listRef?.current && containerToUse.firstChild instanceof HTMLElement) {
          const innerScrollableElement = containerToUse.firstChild;
          scrollHeight = innerScrollableElement.scrollHeight;
          // clientHeight should remain that of the viewport (outer container)
      }

      const atBottom = scrollHeight - scrollTop - clientHeight < threshold;
      setIsAtBottom(atBottom);
      if (atBottom) {
        setShowNewMessagesChip(false);
      }
    }
  }, [listRef]); // Added listRef

  useEffect(() => {
    const container = scrollableContainerRef.current;
    // If using FixedSizeList, its onScroll prop should call handleScroll.
    // If not, and it's a regular element, add listener here.
    if (container && !listRef?.current) { // Only add if not controlled by FixedSizeList's onScroll
      container.addEventListener('scroll', handleScroll, { passive: true });
      handleScroll({ currentTarget: container } as unknown as Event); // Initial check, cast to satisfy type
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll, listRef]);

  const scrollToBottom = useCallback((behavior: ScrollBehavior = 'smooth', count?: number) => {
    const currentItemCount = count ?? itemCount ?? 0;
    if (listRef?.current && currentItemCount > 0) {
      // Enhanced scroll behavior for Tailwind v4.1 snap utilities
      // Use 'end' alignment to work with snap-end behavior
      const align = behavior === 'smooth' ? 'end' : 'auto';
      
      // For better snap behavior, scroll to the last item with 'end' alignment
      // This works well with snap-y snap-end utilities
      listRef.current.scrollToItem(currentItemCount - 1, align);
      
      // Additional smooth scroll enhancement for snap behavior
      if (behavior === 'smooth' && scrollableContainerRef.current) {
        // Small delay to ensure snap points are respected
        setTimeout(() => {
          if (scrollableContainerRef.current) {
            scrollableContainerRef.current.scrollTo({
              top: scrollableContainerRef.current.scrollHeight,
              behavior: 'smooth'
            });
          }
        }, 50);
      }
    } else if (scrollableContainerRef.current) { // Fallback for non-list scenarios
      scrollableContainerRef.current.scrollTo({
        top: scrollableContainerRef.current.scrollHeight,
        behavior: behavior,
      });
    }
    setIsAtBottom(true);
    setShowNewMessagesChip(false);
  }, [listRef, itemCount]); // itemCount dependency

  return {
    scrollableContainerRef, // This ref is for the scrollable element itself (FixedSizeList's outerRef)
    isAtBottom,
    showNewMessagesChip,
    setShowNewMessagesChip,
    scrollToBottom,
    handleScroll // Expose for FixedSizeList's onScroll prop
  };
}
