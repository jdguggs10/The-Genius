// web-app/src/hooks/useTheme.ts
import { useEffect, useState, useCallback } from 'react';

type Theme = 'light' | 'dark' | 'system';

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('theme') as Theme) || 'system';
    }
    return 'system';
  });

  const applyTheme = useCallback((selectedTheme: Theme) => {
    if (typeof window === 'undefined') return; // Guard against SSR or build-time execution

    if (selectedTheme === 'system') {
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', systemPrefersDark);
    } else {
      document.documentElement.classList.toggle('dark', selectedTheme === 'dark');
    }
  }, []);

  useEffect(() => {
    applyTheme(theme);
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', theme);
    }
  }, [theme, applyTheme]);

  // Listen for system theme changes if 'system' is selected
  useEffect(() => {
    if (typeof window === 'undefined' || theme !== 'system') {
      return;
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => applyTheme('system'); // Re-apply 'system' which checks media query

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme, applyTheme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  return { theme, setTheme };
}
