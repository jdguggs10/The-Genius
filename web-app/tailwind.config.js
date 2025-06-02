/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
      fontFamily: {
        headline: ['Snell Roundhand', 'Dancing Script', 'cursive'],
        button: ['Futura', 'Avenir Next', 'AvenirNext-Bold', 'system-ui', 'sans-serif'],
        system: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'SF Pro Text', 'system-ui', 'sans-serif'],
        sans: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'SF Pro Text', 'system-ui', 'sans-serif']
      },
      colors: {
        // Chat bubble colors
        bubble: {
          incoming: 'var(--color-bubble-incoming)',
          outgoing: 'var(--color-bubble-outgoing)',
          warning: 'var(--color-bubble-warning)'
        },
        // App-wide theming colors
        app: {
          bg: 'var(--color-app-bg)',
          'bg-dark': 'var(--color-app-bg-dark)',
          text: 'var(--color-app-text)',
          'text-dark': 'var(--color-app-text-dark)',
          'text-muted': 'var(--color-app-text-muted)',
          'text-muted-dark': 'var(--color-app-text-muted-dark)'
        },
        // Interactive element colors using CSS variables
        primary: {
          50: 'var(--color-primary-50)',
          100: 'var(--color-primary-100)',
          300: 'var(--color-primary-300)',
          400: 'var(--color-primary-400)',
          500: 'var(--color-primary-500)',
          600: 'var(--color-primary-600)',
          700: 'var(--color-primary-700)'
        },
        // Surface colors for cards, inputs, etc.
        surface: {
          'card-light': 'var(--color-surface-card-light)',
          'card-dark': 'var(--color-surface-card-dark)',
          'input-light': 'var(--color-surface-input-light)',
          'input-dark': 'var(--color-surface-input-dark)',
          'border-light': 'var(--color-surface-border-light)',
          'border-dark': 'var(--color-surface-border-dark)'
        }
      },
      // Typography plugin customization using @theme tokens
      typography: {
        DEFAULT: {
          css: {
            '--tw-prose-body': 'var(--color-prose-body)',
            '--tw-prose-headings': 'var(--color-prose-headings)',
            '--tw-prose-lead': 'var(--color-prose-body)',
            '--tw-prose-links': 'var(--color-prose-links)',
            '--tw-prose-bold': 'var(--color-prose-bold)',
            '--tw-prose-counters': 'var(--color-prose-counters)',
            '--tw-prose-bullets': 'var(--color-prose-bullets)',
            '--tw-prose-hr': 'var(--color-prose-hr)',
            '--tw-prose-quotes': 'var(--color-prose-quotes)',
            '--tw-prose-quote-borders': 'var(--color-prose-quote-borders)',
            '--tw-prose-captions': 'var(--color-prose-captions)',
            '--tw-prose-code': 'var(--color-prose-code)',
            '--tw-prose-pre-code': 'var(--color-prose-pre-code)',
            '--tw-prose-pre-bg': 'var(--color-prose-pre-bg)',
            '--tw-prose-th-borders': 'var(--color-prose-th-borders)',
            '--tw-prose-td-borders': 'var(--color-prose-td-borders)',
            // Enhanced styling for chat bubbles
            'p': {
              marginTop: '0.5rem',
              marginBottom: '0.5rem',
            },
            'h1, h2, h3, h4, h5, h6': {
              marginTop: '1rem',
              marginBottom: '0.5rem',
            },
            'ul, ol': {
              marginTop: '0.5rem',
              marginBottom: '0.5rem',
            },
            'code': {
              backgroundColor: 'var(--color-prose-pre-bg)',
              borderRadius: '0.25rem',
              padding: '0.125rem 0.25rem',
              fontSize: '0.875em',
            },
            'pre': {
              backgroundColor: 'var(--color-prose-pre-bg)',
              borderRadius: '0.5rem',
              padding: '1rem',
              marginTop: '0.75rem',
              marginBottom: '0.75rem',
            }
          }
        },
        invert: {
          css: {
            '--tw-prose-body': 'var(--color-prose-body-dark)',
            '--tw-prose-headings': 'var(--color-prose-headings-dark)',
            '--tw-prose-lead': 'var(--color-prose-body-dark)',
            '--tw-prose-links': 'var(--color-prose-links-dark)',
            '--tw-prose-bold': 'var(--color-prose-bold-dark)',
            '--tw-prose-counters': 'var(--color-prose-counters-dark)',
            '--tw-prose-bullets': 'var(--color-prose-bullets-dark)',
            '--tw-prose-hr': 'var(--color-prose-hr-dark)',
            '--tw-prose-quotes': 'var(--color-prose-quotes-dark)',
            '--tw-prose-quote-borders': 'var(--color-prose-quote-borders-dark)',
            '--tw-prose-captions': 'var(--color-prose-captions-dark)',
            '--tw-prose-code': 'var(--color-prose-code-dark)',
            '--tw-prose-pre-code': 'var(--color-prose-pre-code-dark)',
            '--tw-prose-pre-bg': 'var(--color-prose-pre-bg-dark)',
            '--tw-prose-th-borders': 'var(--color-prose-th-borders-dark)',
            '--tw-prose-td-borders': 'var(--color-prose-td-borders-dark)',
            'code': {
              backgroundColor: 'var(--color-prose-pre-bg-dark)',
            },
            'pre': {
              backgroundColor: 'var(--color-prose-pre-bg-dark)',
            }
          }
        }
      }
    }
  },
  plugins: [
    require("daisyui"),
    require('@tailwindcss/typography')
  ],
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/theming/themes")["light"],
          "primary": "var(--color-primary-500)",
          "primary-content": "#ffffff",
        },
        dark: {
          ...require("daisyui/src/theming/themes")["dark"],
          "base-100": "var(--color-surface-card-dark)",
          "base-200": "#171717",
          "primary": "var(--color-primary-600)",
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