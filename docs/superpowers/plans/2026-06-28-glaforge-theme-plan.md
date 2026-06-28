# glaforge.dev Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the dashboard stylesheet to convert the app into a clean, authentic light-themed portal matching the aesthetics, colors, borders, and typography of glaforge.dev.

**Architecture:** Redefine the CSS custom properties in the `:root` pseudo-class to map layout colors directly to Guillaume's colors. Restructure card layouts, sidebar, buttons, and badges to fit the light background and bold serif heading typography.

**Tech Stack:** Vanilla CSS, Google Fonts, HTML.

## Global Constraints
- Target layout: Authentic Light Theme
- Font imports: `PT Sans` (sans-serif) and `Roboto Slab` (serif)
- Root colors: Bordeaux (`#817`), Red (`#a35`), Violet (`#639`), Dark Blue (`#36b`), Light Gray (`#EEE`), White (`#FFF`).
- Border image gradient: `linear-gradient(90deg, #a35, #36b)`

---

### Task 1: Redesign index.css Tokens and Core Typography

**Files:**
- Modify: `job_scraper/index.css`

**Interfaces:**
- Produces: CSS properties and overrides applied to the entire application.

- [ ] **Step 1: Replace :root design tokens and import Google Fonts**
  Open [index.css](file:///C:/Users/deept/ai-job-search/job_scraper/index.css).
  Add the `@import` statement at the top of the file to fetch the fonts:
  ```css
  @import url('https://fonts.googleapis.com/css2?family=PT+Sans:ital,wght@0,400;0,700;1,400;1,700&family=Roboto+Slab:wght@800&display=swap');
  ```
  Replace lines 1 to 33 (`:root` definition) with the new theme tokens:
  ```css
  :root {
      /* glaforge.dev Color Palette */
      --bordeaux: #817;
      --red: #a35;
      --pink: #c66;
      --orange: #e94;
      --yellow: #ed0;
      --applegreen: #9d5;
      --emeraldgreen: #4d8;
      --cyan: #0bc;
      --lightblue: #09c;
      --darkblue: #36b;
      --violet: #639;
      --lightgray: #EEE;

      /* Semantic Mappings */
      --bg-base: #fafafa;
      --bg-surface: #ffffff;
      --bg-surface-hover: #fcfcfc;
      --bg-sidebar: #EEEEEE;
      --bg-glass: rgba(255, 255, 255, 0.95);
      --bg-input: #ffffff;
      
      --border-light: #e5e7eb;
      --border-medium: #d1d5db;
      --border-hover: var(--darkblue);
      --border-focus: var(--red);
      
      --text-primary: #111827;
      --text-secondary: #4b5563;
      --text-muted: #6b7280;
      
      --accent-high: var(--red);
      --accent-high-glow: rgba(163, 53, 85, 0.08);
      --accent-medium: var(--darkblue);
      --accent-medium-glow: rgba(51, 102, 187, 0.08);
      --accent-low: var(--violet);
      --accent-low-glow: rgba(99, 57, 153, 0.08);
      --accent-applied: var(--bordeaux);
      --accent-applied-glow: rgba(129, 17, 119, 0.08);
      --accent-danger: var(--red);
      
      --gradient-primary: linear-gradient(90deg, var(--red), var(--darkblue));
      --gradient-glow: radial-gradient(circle, rgba(163, 53, 85, 0.05) 0%, transparent 70%);
      --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
      --transition-smooth: all 0.25s ease-in-out;
  }
  ```

- [ ] **Step 2: Apply gradient page border and global typography overrides**
  Modify global body and HTML parameters to apply the top/bottom gradient borders and font mappings.
  Set:
  ```css
  html {
      border-top: var(--violet) 1rem solid;
      border-image: linear-gradient(90deg, var(--red), var(--darkblue)) 1;
      border-bottom: var(--violet) 1rem solid;
      box-sizing: border-box;
      margin: 0;
      padding: 0;
  }
  body {
      font-family: 'PT Sans', sans-serif;
      background-color: var(--bg-base);
      color: var(--text-primary);
      min-height: 100vh;
      line-height: 1.5;
  }
  h1, h2, h3, h4, h5, h6 {
      font-family: 'Roboto Slab', serif;
      font-weight: 800;
      color: var(--text-primary);
  }
  ```

- [ ] **Step 3: Redesign Sidebar, Cards, and Components**
  Redesign the cards to use clean borders and remove box shadows or neon lines.
  - Set the `.sidebar` background to `var(--bg-sidebar)` (solid `#EEE` style).
  - Set `.job-card` styles:
    ```css
    .job-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-light);
        border-radius: 12px;
        box-shadow: var(--card-shadow);
    }
    .job-card:hover {
        border-color: var(--border-hover);
        transform: translateY(-2px);
    }
    /* Dynamic fit highlights */
    .job-card.fit-high {
        border-left: 6px solid var(--red);
    }
    .job-card.fit-medium {
        border-left: 6px solid var(--darkblue);
    }
    .job-card.fit-low {
        border-left: 6px solid var(--violet);
    }
    ```
  - Style buttons:
    ```css
    .btn-primary {
        background-color: var(--red);
        color: #ffffff;
        border: none;
    }
    .btn-primary:hover {
        background-color: var(--bordeaux);
    }
    .btn-success {
        background-color: var(--darkblue);
        color: #ffffff;
        border: none;
    }
    .btn-success:hover {
        background-color: #248;
    }
    ```
  - Style dividers:
    ```css
    hr, .divider {
        border: 0;
        border-top: var(--violet) 3px dashed;
        margin: 1.5rem 0;
    }
    ```

- [ ] **Step 4: Commit changes**
  ```bash
  git add job_scraper/index.css
  git commit -m "style: apply glaforge.dev authentic light theme layout to index.css"
  ```

---

### Task 2: UI Check and Layout Verification

**Files:**
- Modify: `job_scraper/index.html`

- [ ] **Step 1: Check UI compatibility**
  Verify that font classes and titles align. Ensure there are no residual inline styles in `index.html` that enforce dark mode or make text unreadable on a light background.
  Adjust the lock/auth wrapper background in CSS or HTML to look clean and styled.

- [ ] **Step 2: Commit validation**
  ```bash
  git add job_scraper/index.html
  git commit -m "style: verify and align UI components in index.html for light theme"
  ```
