# Portfolio Icon Toggle and Blur Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modify the portfolio HTML layout to include Font Awesome CSS CDN, disable scanlines overlay in light mode, and update the JavaScript state management to toggle sun/moon icons.

**Architecture:** Add stylesheet link to `<head>`. Update CSS rules and JS label helper. Deploy to GitHub Pages and Vercel.

**Tech Stack:** HTML5, CSS3, Vanilla JS, Vercel CLI.

## Global Constraints
*   Ensure Font Awesome CDN loads correctly.
*   Retain existing `.light-mode` custom properties.
*   Ensure desktop button follows custom formatting: `[ 🌙 ]` / `[ ☀️ ]`.

---

### Task 1: Clone Repository and Code Modifications

**Files:**
*   Create: `C:\Users\deept\temp-deepthakkar\index.html` (via git clone)
*   Modify: `C:\Users\deept\temp-deepthakkar\index.html`

**Interfaces:**
*   Produces: Portfolio index.html with icons and blur fix.

- [ ] **Step 1: Clone the deepthakkar repository**
  Run: `git clone https://github.com/imdeepthakkar/deepthakkar.git C:\Users\deept\temp-deepthakkar`

- [ ] **Step 2: Add Font Awesome CDN Link to head**
  Modify: `C:\Users\deept\temp-deepthakkar\index.html`
  Find lines 6-7:
  ```html
  <title>Deep Thakkar — Technical Lead</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400&display=swap" rel="stylesheet">
  ```
  Insert the Font Awesome CDN link next to it:
  ```html
  <title>Deep Thakkar — Technical Lead</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  ```

- [ ] **Step 3: Disable scanlines overlay in light mode**
  Modify: `C:\Users\deept\temp-deepthakkar\index.html`
  Find the CSS variables block for `body.light-mode` (around lines 681-697):
  ```css
    body.light-mode {
      --bg: #f8fafc;
      /* ... */
      --cursor: #ea580c;
    }
  ```
  Append the following rule immediately after it:
  ```css
    body.light-mode::before {
      display: none;
    }
  ```

- [ ] **Step 4: Update Toggle Button Markup**
  Modify: `C:\Users\deept\temp-deepthakkar\index.html`
  Find the topbar theme toggle button (around line 720):
  ```html
      <a href="#" id="theme-toggle" onclick="toggleTheme(event)" style="color:var(--orange);border:1px solid rgba(249,115,22,0.4);background:rgba(249,115,22,0.08);margin-left:8px;">[ light_mode ]</a>
  ```
  Replace with:
  ```html
      <a href="#" id="theme-toggle" onclick="toggleTheme(event)" style="color:var(--orange);border:1px solid rgba(249,115,22,0.4);background:rgba(249,115,22,0.08);margin-left:8px;">[ <i class="fa-solid fa-moon"></i> ]</a>
  ```

  Find the mobile theme toggle button (around line 734):
  ```html
    <a href="#" id="mobile-theme-toggle" class="pdf-link" onclick="toggleTheme(event);closeMenu()" style="border-top:1px solid var(--border);">[ light_mode ]</a>
  ```
  Replace with:
  ```html
    <a href="#" id="mobile-theme-toggle" class="pdf-link" onclick="toggleTheme(event);closeMenu()" style="border-top:1px solid var(--border);">$ <i class="fa-solid fa-moon"></i></a>
  ```

- [ ] **Step 5: Update JavaScript Theme Labels logic**
  Modify: `C:\Users\deept\temp-deepthakkar\index.html`
  Find the `updateThemeToggleLabels(isLight)` function (around lines 1099-1106):
  ```javascript
  function updateThemeToggleLabels(isLight) {
    const toggleBtn = document.getElementById('theme-toggle');
    const mobileToggleBtn = document.getElementById('mobile-theme-toggle');
    const label = isLight ? '[ dark_mode ]' : '[ light_mode ]';
    
    if (toggleBtn) toggleBtn.textContent = label;
    if (mobileToggleBtn) mobileToggleBtn.textContent = label;
  }
  ```
  Replace with:
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

- [ ] **Step 6: Commit local updates**
  Run: `git commit -am "feat: add Font Awesome icons to theme toggle and disable scanlines in light mode"`

---

### Task 2: Push, Backup, and Deploy

**Files:**
*   Modify: `C:\Users\deept\deepthakkar\portfolio.html`
*   Modify: `C:\Users\deept\deepthakkar\vercel.json`

**Interfaces:**
*   Consumes: Updated index.html from Task 1.
*   Produces: Pushed changes on remote GitHub repository and updated Vercel deployment.

- [ ] **Step 1: Push updates to GitHub**
  Run: `git push origin main` in `C:\Users\deept\temp-deepthakkar`

- [ ] **Step 2: Update local backups in Downloads**
  Run: `Copy-Item C:\Users\deept\temp-deepthakkar\index.html C:\Users\deept\Downloads\index.html -Force`
  Run: `Copy-Item C:\Users\deept\temp-deepthakkar\index.html C:\Users\deept\Downloads\deep-thakkar-portfolio_5.html -Force`

- [ ] **Step 3: Update file in Vercel project directory**
  Run: `Copy-Item C:\Users\deept\temp-deepthakkar\index.html C:\Users\deept\deepthakkar\portfolio.html -Force`

- [ ] **Step 4: Clean up temporary clone**
  Run: `Remove-Item -Recurse -Force C:\Users\deept\temp-deepthakkar`

- [ ] **Step 5: Redeploy Vercel**
  Run: `npx vercel --prod` in `C:\Users\deept\deepthakkar`
