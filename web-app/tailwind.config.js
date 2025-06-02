/** @type {import('tailwindcss').Config} */
export default {
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/theming/themes")["light"],
          "primary": "#3b82f6", // blue-500
          "primary-content": "#ffffff",
        },
        dark: {
          ...require("daisyui/src/theming/themes")["dark"],
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