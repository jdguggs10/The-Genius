# Tailwind CSS v4 Migration

This project has been successfully migrated from Tailwind CSS v3 to v4, adopting the new CSS-first configuration approach.

## What Changed

### 1. **CSS-First Configuration**
- Removed JavaScript-based theme configuration from `tailwind.config.js`
- Added `@theme` blocks in CSS for design tokens
- Migrated to `@import "tailwindcss"` syntax

### 2. **Vite Plugin Integration**
- Replaced PostCSS-based setup with the official `@tailwindcss/vite` plugin
- Removed `postcss.config.js` (no longer needed)
- Added `tailwindcss()` plugin to `vite.config.ts`

### 3. **Theme Configuration**
Font families are now defined using CSS custom properties:

```css
@theme {
  --font-family-headline: 'Snell Roundhand', 'Dancing Script', cursive;
  --font-family-system: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', system-ui, sans-serif;
  --font-family-button: 'Futura', 'Avenir Next', 'AvenirNext-Bold', system-ui, sans-serif;
  --font-family-sans: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', system-ui, sans-serif;
}
```

### 4. **Custom Variants**
Dark mode is now handled with a custom variant:

```css
@custom-variant dark .dark &;
```

### 5. **Plugin Configuration**
Minimal `tailwind.config.js` kept only for DaisyUI plugin configuration:

```js
export default {
  plugins: [require("daisyui")],
  daisyui: {
    // ... existing DaisyUI configuration
  }
}
```

## Benefits of v4

1. **Performance**: 3-5× faster full builds, 100×+ faster HMR updates
2. **CSS-First**: Design tokens defined directly in stylesheets
3. **Modern CSS**: Built on Lightning CSS with better browser support
4. **Automatic Discovery**: No need for `content` array in config
5. **Type Safety**: Theme variables registered with `@property`

## Usage

### Font Families
Use the new Tailwind utilities:
- `font-headline` → custom headline font
- `font-system` → system font
- `font-button` → button font
- `font-sans` → default sans serif (system font)

### Development
```bash
npm run dev    # Fast HMR with Oxide engine
npm run build  # Optimized production build
```

### Adding New Design Tokens
Add custom properties directly in CSS:

```css
@theme {
  --color-brand: #3b82f6;
  --spacing-custom: 2.5rem;
}
```

## Migration Notes

- DaisyUI themes still configured in JavaScript (plugin requirement)
- Backward compatibility maintained with existing CSS custom properties
- All existing Tailwind utilities work the same way
- Dark mode implementation unchanged (`dark:` prefix still works)

## Performance Improvements

With v4's Oxide engine:
- Initial builds are significantly faster
- HMR updates are nearly instantaneous
- Better CSS optimization and tree-shaking
- Reduced bundle sizes through Lightning CSS 