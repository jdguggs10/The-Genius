/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  // Safelist dynamic or conditional classes used in JSX templates
  safelist: [
    { pattern: /^(bg|text|border|from|to)-/ },
    { pattern: /^dark:/ }
  ],
  theme: {
    extend: {
      fontFamily: {
        'headline': ['var(--font-headline)'],
        'system': ['var(--font-system)'],
        'button': ['var(--font-button)'],
        'sans': ['var(--font-system)'], // This makes system font the default
      },
    },
  },
  darkMode: 'class', // This line enables class-based dark mode
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/theming/themes")["light"],
          // Customize to match your current colors
          "primary": "#3b82f6", // Your blue-500
          "primary-content": "#ffffff",
        },
        dark: {
          ...require("daisyui/src/theming/themes")["dark"],
          // Customize to match your current dark theme
          "base-100": "#262626", // neutral-800
          "base-200": "#171717", // neutral-900
          "primary": "#2563eb", // blue-600
          "primary-content": "#ffffff",
        }
      }
    ],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
  }
}
