// web-app/src/hooks/useTheme.test.ts
import { renderHook, act } from '@testing-library/react';
import { useTheme } from './useTheme';

describe('useTheme', () => {
  const mockMatchMedia = (matches: boolean) => {
    return vi.fn().mockImplementation(query => ({
        matches: matches, // query === '(prefers-color-scheme: dark)' ? matches : false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
    }));
  }

  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark');
    // Default matchMedia mock (prefers light)
    vi.stubGlobal('matchMedia', mockMatchMedia(false));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should initialize with system theme by default if no localStorage', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('system');
  });

  it('should initialize with theme from localStorage', () => {
    localStorage.setItem('theme', 'dark');
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('should change theme and update localStorage and document class', () => {
    const { result } = renderHook(() => useTheme());
    act(() => {
      result.current.setTheme('light');
    });
    expect(result.current.theme).toBe('light');
    expect(localStorage.getItem('theme')).toBe('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);

    act(() => {
      result.current.setTheme('dark');
    });
    expect(result.current.theme).toBe('dark');
    expect(localStorage.getItem('theme')).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('applies dark class if system theme is dark and theme is "system"', () => {
    vi.stubGlobal('matchMedia', mockMatchMedia(true)); // System prefers dark

    localStorage.setItem('theme', 'system'); // Hook will read this
    renderHook(() => useTheme()); // This will call applyTheme internally via useEffect

    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('applies light class if system theme is light and theme is "system"', () => {
    vi.stubGlobal('matchMedia', mockMatchMedia(false)); // System prefers light

    localStorage.setItem('theme', 'system');
    renderHook(() => useTheme());

    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('updates display when system theme changes and current theme is "system"', () => {
    let mediaQueryChangeCallback: (() => void) | null = null;
    const matchMediaMockWithListener = vi.fn().mockImplementation(query => ({
        matches: false, // Initially prefers light
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: (_event: string, cb: () => void) => { mediaQueryChangeCallback = cb; }, // Capture callback
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
    }));
    vi.stubGlobal('matchMedia', matchMediaMockWithListener);

    localStorage.setItem('theme', 'system');
    renderHook(() => useTheme());
    expect(document.documentElement.classList.contains('dark')).toBe(false); // Initial: system is light

    // Simulate system theme changing to dark
    act(() => {
      // Update the mock to reflect system preference for dark
      (matchMediaMockWithListener as vi.Mock).mockImplementation(query => ({
        matches: true, // Now prefers dark
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: (_event: string, cb: () => void) => { mediaQueryChangeCallback = cb; },
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }));
      if(mediaQueryChangeCallback) {
        mediaQueryChangeCallback(); // Trigger the captured change handler
      }
    });

    expect(document.documentElement.classList.contains('dark')).toBe(true); // Should now be dark
  });
});
