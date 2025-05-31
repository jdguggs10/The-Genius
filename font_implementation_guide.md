# Font Implementation Guide for The Genius Web App

> **Goal:** Implement custom fonts for headlines (Snell Roundhand), UI text (San Francisco), and buttons (Futura/AvenirNext)

This guide will walk you through implementing these fonts step-by-step with a GUI-focused approach.

## 📋 Font Stack Overview

- **Headline:** Snell Roundhand (with Dancing Script web fallback)
- **UI text:** San Francisco via system fonts
- **Buttons:** Futura-Bold or AvenirNext-Bold

## Step 1: Update CSS File with Font Definitions

**📁 Navigate to:** `web-app/src/index.css`

1. **Click** on the `index.css` file to open it in your editor
2. **Find** this line (around line 1):
   ```css
   @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
   ```
3. **Replace** that entire line with:
   ```css
   @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Dancing+Script:wght@400;700&display=swap');
   ```

4. **Scroll down** to the `:root` section (around line 5-6)
5. **Find** this line:
   ```css
   font-family: 'Inter', system-ui, Avenir, Helvetica, Arial, sans-serif;
   ```
6. **Add** these lines **right after** the font-family line:
   ```css
   
   /* Custom font definitions */
   --font-headline: 'Snell Roundhand', 'Dancing Script', cursive;
   --font-system: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', system-ui, sans-serif;
   --font-button: 'Futura', 'Avenir Next', 'AvenirNext-Bold', system-ui, sans-serif;
   ```

7. **Save** the file (Ctrl+S or Cmd+S)

## Step 2: Update Tailwind Configuration

**📁 Navigate to:** `web-app/tailwind.config.js`

1. **Click** on `tailwind.config.js` to open it
2. **Find** the `theme` section (around line 10):
   ```javascript
   theme: {
     extend: {},
   },
   ```
3. **Replace** the `extend: {}` part with:
   ```javascript
   extend: {
     fontFamily: {
       'headline': ['var(--font-headline)'],
       'system': ['var(--font-system)'],
       'button': ['var(--font-button)'],
       'sans': ['var(--font-system)'], // This makes system font the default
     },
   },
   ```

4. **Save** the file (Ctrl+S or Cmd+S)

## Step 3: Update Chat Header

**📁 Navigate to:** `web-app/src/components/chat.tsx`

1. **Click** on `chat.tsx` to open it
2. **Press** Ctrl+F (or Cmd+F) to open search
3. **Search for:** `<h1 className="text-base sm:text-lg font-semibold`
4. **Find** this line:
   ```jsx
   <h1 className="text-base sm:text-lg font-semibold text-gray-800 dark:text-neutral-200">The Genius</h1>
   ```
5. **Replace** it with:
   ```jsx
   <h1 className="text-base sm:text-lg font-headline font-bold text-gray-800 dark:text-neutral-200">The Genius</h1>
   ```

## Step 4: Update Send Button

**📝 Still in:** `web-app/src/components/chat.tsx`

1. **Search for:** `className="p-2 sm:p-3 bg-gradient`
2. **Find** the send button (around line 300+) - it should look like this:
   ```jsx
   className="p-2 sm:p-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg sm:rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all transform hover:scale-105 active:scale-95 shadow-lg dark:from-blue-600 dark:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800"
   ```
3. **Add** `font-button font-bold` to the end:
   ```jsx
   className="p-2 sm:p-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-lg sm:rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-all transform hover:scale-105 active:scale-95 shadow-lg dark:from-blue-600 dark:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800 font-button font-bold"
   ```

## Step 5: Update Theme Toggle Button

**📝 Still in:** `web-app/src/components/chat.tsx`

1. **Search for:** `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`
2. **Find** the theme toggle button className:
   ```jsx
   className="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-neutral-700 text-gray-600 dark:text-gray-300 transition-colors"
   ```
3. **Add** `font-button` to the end:
   ```jsx
   className="p-1.5 rounded-md hover:bg-gray-200 dark:hover:bg-neutral-700 text-gray-600 dark:text-gray-300 transition-colors font-button"
   ```

## Step 6: Test Your Changes

### Start Development Server

1. **Open Terminal/Command Prompt**
2. **Navigate** to your web-app folder:
   ```bash
   cd web-app
   ```
3. **Start** the development server:
   ```bash
   pnpm run dev
   ```
4. **Open** your browser and go to: `http://localhost:5173`

### What You Should See

✅ **"The Genius" title:** Now displays in cursive font (Snell Roundhand on Mac, Dancing Script elsewhere)

✅ **All UI text:** Uses system fonts (San Francisco on Mac/iOS, system fonts elsewhere)

✅ **Buttons:** Use Futura/Avenir Next when available, fall back to system fonts

## 🎨 Optional: Add More Headlines

To style other text as headlines, add `font-headline` to any element:

```jsx
<h2 className="font-headline text-xl">Your Headline Here</h2>
<p className="font-headline text-lg">Cursive subtitle</p>
```

## 🛠️ Troubleshooting

### Fonts Don't Appear
1. **Hard refresh** browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. **Check** that all files are saved
3. **Restart** development server:
   - Press Ctrl+C in terminal to stop
   - Run `pnpm run dev` again

### Getting Errors
1. **Double-check** all commas and brackets are correct
2. **Verify** you didn't accidentally delete existing code
3. **Copy-paste** examples exactly as shown
4. **Check** terminal for specific error messages

### Font Availability by System

| System | Headline Font | UI Font | Button Font |
|--------|---------------|---------|-------------|
| **Mac/iOS** | Snell Roundhand | San Francisco | Futura |
| **Windows** | Dancing Script | Segoe UI | Arial Black |
| **Android** | Dancing Script | Roboto | Roboto Bold |
| **Linux** | Dancing Script | System Sans | System Sans Bold |

## 📝 Final Notes

- Fonts automatically adapt to each user's device
- Web fonts (Dancing Script) load from Google Fonts
- System fonts provide the best performance
- Fallbacks ensure your app looks good everywhere

**🎉 You're done!** Your app now has beautiful, platform-appropriate typography that enhances the user experience across all devices.