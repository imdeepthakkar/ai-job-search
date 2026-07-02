# Portfolio Light/Dark Theme Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a light mode/dark mode toggle button to the portfolio website so users can switch themes, with state persistence and no style flashes on load.

**Architecture:** Toggle a `.light-mode` class on the `<body>` element. Set light-theme values for CSS variables inside `body.light-mode`. Persist choice in `localStorage`.

**Tech Stack:** HTML5, CSS Custom Properties, Vanilla JavaScript.

## Global Constraints
*   Do not break existing CSS custom variables.
*   Deepened colors in light mode must maintain Web Content Accessibility Guidelines (WCAG) contrast ratios.
*   Buttons must use standard terminal formatting style: `[ light_mode ]` and `[ dark_mode ]`.

---

### Task 1: Repository Clone and HTML Modifications

**Files:**
*   Create: `C:\Users\deept\temp-deepthakkar\index.html` (via git clone)
*   Modify: `C:\Users\deept\temp-deepthakkar\index.html`

**Interfaces:**
*   Produces: HTML skeleton with theme toggle elements and early head script.

- [ ] **Step 1: Clone the deepthakkar repository**
  Run command: `git clone https://github.com/imdeepthakkar/deepthakkar.git C:\Users\deept\temp-deepthakkar`

- [ ] **Step 2: Add early inline script inside `<body>`**
  Modify: `C:\Users\deept\temp-deepthakkar\index.html`
  Insert the following script block immediately after the opening `<body>` tag (around line 679) to apply the saved theme before the page starts rendering:
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

- [ ] **Step 3: Add toggle button to navigation bar**
  Modify: `C:\Users\deept\temp-deepthakkar\index.html`
  Find the navigation block `<nav>` (around line 691-697):
  ```html
    <nav>
      <a href="#experience">experience</a>
      <a href="#skills">skills</a>
      <a href="#certs">certs</a>
      <a href="#contact">contact</a>
      <a href="#" onclick="exportPDF(event)" style="color:var(--orange);border:1px solid rgba(249,115,22,0.4);background:rgba(249,115,22,0.08);">⬇ save as pdf</a>
    </nav>
  ```
  Insert the new anchor tag next to "save as pdf" (immediately before `</nav>`):
  ```html
      <a href="#" id="theme-toggle" onclick="toggleTheme(event)" style="color:var(--orange);border:1px solid rgba(249,115,22,0.4);background:rgba(249,115,22,0.08);margin-left:8px;">[ light_mode ]</a>
  ```

- [ ] **Step 4: Add toggle button to mobile navigation**
  Modify: `C:\Users\deept\temp-deepthakkar\index.html`
  Find the mobile nav block `<div class="mobile-nav" id="mobile-nav">` (around line 704-710):
  ```html
  <div class="mobile-nav" id="mobile-nav">
    <a href="#experience" onclick="closeMenu()">$ experience</a>
    <a href="#skills" onclick="closeMenu()">$ skills</a>
    <a href="#certs" onclick="closeMenu()">$ certs</a>
    <a href="#contact" onclick="closeMenu()">$ contact</a>
    <a href="#" class="pdf-link" onclick="exportPDF(event);closeMenu()">⬇ save as pdf</a>
  </div>
  ```
  Insert the new anchor tag next to "save as pdf" (immediately before `</div>`):
  ```html
    <a href="#" id="mobile-theme-toggle" class="pdf-link" onclick="toggleTheme(event);closeMenu()" style="border-top:1px solid var(--border);">[ light_mode ]</a>
  ```

- [ ] **Step 5: Verify syntax and commit changes**
  Run: `git diff` inside `C:\Users\deept\temp-deepthakkar`
  Run: `git commit -am "feat: add theme toggle html markup and early script"`

---

### Task 2: CSS Light Mode Styling

**Files:**
*   Modify: `C:\Users\deept\temp-deepthakkar\index.html`

**Interfaces:**
*   Consumes: HTML elements from Task 1.
*   Produces: Styles defining properties for `body.light-mode`.

- [ ] **Step 1: Add the light-mode CSS rules**
  Modify: `C:\Users\deept\temp-deepthakkar\index.html`
  Find the closing `</style>` tag (around line 677). Insert the following CSS rules immediately before it:
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

- [ ] **Step 2: Commit the stylesheet updates**
  Run: `git commit -am "feat: add CSS variables for light-mode theme"`

---

### Task 3: JavaScript State Management

**Files:**
*   Modify: `C:\Users\deept\temp-deepthakkar\index.html`

**Interfaces:**
*   Consumes: UI button IDs `theme-toggle` and `mobile-theme-toggle`.
*   Produces: Active JavaScript event handlers and load listeners.

- [ ] **Step 1: Add JavaScript theme toggle and load listener**
  Modify: `C:\Users\deept\temp-deepthakkar\index.html`
  Find the closing `</script>` tag at the very bottom of the document. Add the following functions immediately before the closing `</script>` tag (around line 1042):
  ```javascript
  function toggleTheme(e) {
    if (e) e.preventDefault();
    const body = document.body;
    body.classList.toggle('light-mode');
    
    const isLight = body.classList.contains('light-mode');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    
    updateThemeToggleLabels(isLight);
  }

  function updateThemeToggleLabels(isLight) {
    const toggleBtn = document.getElementById('theme-toggle');
    const mobileToggleBtn = document.getElementById('mobile-theme-toggle');
    const label = isLight ? '[ dark_mode ]' : '[ light_mode ]';
    
    if (toggleBtn) toggleBtn.textContent = label;
    if (mobileToggleBtn) mobileToggleBtn.textContent = label;
  }

  document.addEventListener('DOMContentLoaded', () => {
    const isLight = document.body.classList.contains('light-mode');
    updateThemeToggleLabels(isLight);
  });
  ```

- [ ] **Step 2: Commit the JS updates**
  Run: `git commit -am "feat: implement JavaScript logic for theme toggling and persistence"`

---

### Task 4: Local testing, Push and Cleanup

**Files:**
*   Modify: `C:\Users\deept\temp-deepthakkar\index.html`

**Interfaces:**
*   Consumes: Finished site implementation.
*   Produces: Pushed changes on remote repository `deepthakkar` on branch `main`.

- [ ] **Step 1: Test HTML changes locally**
  Locate `C:\Users\deept\temp-deepthakkar\index.html` and verify the document opens and functions correctly.
  
- [ ] **Step 2: Push changes to GitHub repository**
  Run: `git push origin main` in `C:\Users\deept\temp-deepthakkar`

- [ ] **Step 3: Update local backups in Downloads**
  Copy `C:\Users\deept\temp-deepthakkar\index.html` back to your local backup paths:
  Run: `Copy-Item C:\Users\deept\temp-deepthakkar\index.html C:\Users\deept\Downloads\index.html -Force`
  Run: `Copy-Item C:\Users\deept\temp-deepthakkar\index.html C:\Users\deept\Downloads\deep-thakkar-portfolio_5.html -Force`

- [ ] **Step 4: Clean up temporary clone**
  Run: `Remove-Item -Recurse -Force C:\Users\deept\temp-deepthakkar`
