# Design Spec: Portfolio Icon Toggle and Blur Fix

## Status
Approved

## Background & Goals
Based on user feedback:
1.  Light mode text is slightly blurry. This is caused by the `.before` scanline overlay. We will disable scanlines in light mode.
2.  The text-based toggle (`[ light_mode ]` / `[ dark_mode ]`) will be replaced with Font Awesome icons (Sun for light mode, Moon for dark mode).

## Requirements
*   Disable scanlines in light mode to keep text crisp.
*   Add Font Awesome CDN CSS.
*   Update toggle markup and JS to support sun/moon icons.
*   Deploy to GitHub Pages and Vercel.

## Design Details

### 1. Style Changes
In `<style>`, add the following rules:
```css
body.light-mode::before {
  display: none;
}
```

And in `<head>`, add the Font Awesome link:
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

### 2. Markup Changes

#### Navigation bar toggle button
```html
<a href="#" id="theme-toggle" onclick="toggleTheme(event)" style="color:var(--orange);border:1px solid rgba(249,115,22,0.4);background:rgba(249,115,22,0.08);margin-left:8px;">[ <i class="fa-solid fa-moon"></i> ]</a>
```

#### Mobile navigation toggle button
```html
<a href="#" id="mobile-theme-toggle" class="pdf-link" onclick="toggleTheme(event);closeMenu()" style="border-top:1px solid var(--border);">$ <i class="fa-solid fa-moon"></i></a>
```

### 3. JavaScript Changes

Update the label rendering function:
```javascript
function updateThemeToggleLabels(isLight) {
  const toggleBtn = document.getElementById('theme-toggle');
  const mobileToggleBtn = document.getElementById('mobile-theme-toggle');
  
  const desktopHtml = isLight 
    ? '[ <i class="fa-solid fa-sun"></i> ]' 
    : '[ <i class="fa-solid fa-moon"></i> ]';
    
  const mobileHtml = isLight 
    ? '$ <i class="fa-solid fa-sun"></i>' 
    : '$ <i class="fa-solid fa-moon"></i>';
  
  if (toggleBtn) toggleBtn.innerHTML = desktopHtml;
  if (mobileToggleBtn) mobileToggleBtn.innerHTML = mobileHtml;
}
```

## Testing Plan
1. Open the page and verify dark mode is active and shows the moon icon `[ 🌙 ]`.
2. Toggle to light mode. Verify:
   - Background changes to light slate.
   - Text is sharp and crisp (no scanline overlay).
   - Toggle icon changes to the sun icon `[ ☀️ ]`.
3. Refresh the page to verify persistence.
