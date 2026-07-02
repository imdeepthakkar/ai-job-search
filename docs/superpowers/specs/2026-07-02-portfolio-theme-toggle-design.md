# Design Spec: Portfolio Light/Dark Theme Toggle

## Status
Proposed/Approved

## Background & Goals
Add a light mode/dark mode toggle to the personal portfolio website (`https://imdeepthakkar.github.io/deepthakkar/`). The toggle will allow users to switch between a dark terminal theme and a clean, high-contrast light mode theme.

## Requirements
*   A theme toggle button placed in the top navigation bar (`.topbar`) next to the "save as pdf" button.
*   A corresponding item in the mobile dropdown navigation.
*   The button should display `[ light_mode ]` when the theme is dark and `[ dark_mode ]` when the theme is light, fitting the terminal/command-line aesthetic.
*   Theme selection must persist using `localStorage`.
*   Prevent a "flash of dark/light theme" on initial page load by applying the class inline early in the body rendering process.
*   A high-contrast light mode theme that deepens color variables to ensure readability.

## Design Details

### 1. Color Palette (CSS Variables)
In `index.html`, we will override the CSS custom properties when `body.light-mode` is active.

```css
body.light-mode {
  --bg: #f8fafc;
  --bg2: #ffffff;
  --bg3: #f1f5f9;
  --border: #cbd5e1;
  --orange: #ea580c;
  --orange-dim: #c2410c;
  --green: #16a34a;
  --green-dim: #15803d;
  --blue: #2563eb;
  --purple: #7c3aed;
  --yellow: #d97706;
  --red: #dc2626;
  --text: #0f172a;
  --text-dim: #475569;
  --text-muted: #64748b;
  --cursor: #ea580c;
}
```

### 2. HTML Markup changes

#### Topbar Navigation
We will insert the theme toggle button next to the "save as pdf" button:
```html
<a href="#" id="theme-toggle" onclick="toggleTheme(event)" style="color:var(--orange);border:1px solid rgba(249,115,22,0.4);background:rgba(249,115,22,0.08);margin-left:8px;">[ light_mode ]</a>
```

#### Mobile Navigation
We will insert the toggle in the mobile dropdown navigation:
```html
<a href="#" id="mobile-theme-toggle" class="pdf-link" onclick="toggleTheme(event);closeMenu()" style="border-top:1px solid var(--border);">[ light_mode ]</a>
```

### 3. JavaScript Logic

#### Inline Execution Script (placed immediately after `<body>` starts)
This avoids the flash of dark mode when the user preference is set to light mode.
```html
<script>
  (function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      document.body.classList.add('light-mode');
    }
  })();
</script>
```

#### Global Script Logic (in `<script>` at the bottom of the page)
```javascript
function toggleTheme(e) {
  if (e) e.preventDefault();
  const body = document.body;
  body.classList.toggle('light-mode');
  
  const isLight = body.classList.contains('light-mode');
  localStorage.setItem('theme', isLight ? 'light' : 'dark');
  
  // Update button texts
  const toggleBtn = document.getElementById('theme-toggle');
  const mobileToggleBtn = document.getElementById('mobile-theme-toggle');
  const label = isLight ? '[ dark_mode ]' : '[ light_mode ]';
  
  if (toggleBtn) toggleBtn.textContent = label;
  if (mobileToggleBtn) mobileToggleBtn.textContent = label;
}

// Initial label setup on page load
document.addEventListener('DOMContentLoaded', () => {
  const isLight = document.body.classList.contains('light-mode');
  const toggleBtn = document.getElementById('theme-toggle');
  const mobileToggleBtn = document.getElementById('mobile-theme-toggle');
  const label = isLight ? '[ dark_mode ]' : '[ light_mode ]';
  
  if (toggleBtn) toggleBtn.textContent = label;
  if (mobileToggleBtn) mobileToggleBtn.textContent = label;
});
```

## Testing Plan
1. Open the page and verify dark mode loads by default.
2. Click the `[ light_mode ]` toggle. Verify the theme changes to a light background and all text/icons remain highly readable.
3. Verify that the button text changes to `[ dark_mode ]`.
4. Refresh the page. Verify the light mode remains active without flashing dark mode first.
5. Click the toggle again to return to dark mode. Verify it persists after refresh.
6. Test mobile nav toggle behavior under a simulated mobile viewport.
