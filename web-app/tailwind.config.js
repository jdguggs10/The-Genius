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
    extend: {},
  },
  darkMode: 'class', // This line enables class-based dark mode
  plugins: [],
}
