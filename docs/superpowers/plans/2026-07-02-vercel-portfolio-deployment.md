# Vercel Portfolio Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Copy the updated portfolio HTML file into the `deepthakkar` Vercel project, configure `vercel.json` routing, and deploy to production.

**Architecture:** Create `portfolio.html` at the project root. Add `portfolio.html` as a static build in `vercel.json` and map the path `/portfolio` to it. Run deployment using the Vercel CLI.

**Tech Stack:** Vercel CLI, JSON.

## Global Constraints
*   Do not remove existing routes or builds in `vercel.json`.
*   Ensure `/portfolio` maps exactly to `/portfolio.html` static destination.

---

### Task 1: Copy Portfolio File and Configure Vercel

**Files:**
*   Create: `C:\Users\deept\deepthakkar\portfolio.html`
*   Modify: `C:\Users\deept\deepthakkar\vercel.json`

**Interfaces:**
*   Consumes: Local portfolio file `C:\Users\deept\Downloads\index.html`.
*   Produces: Updated Vercel configuration and target HTML file.

- [ ] **Step 1: Copy the portfolio file**
  Run: `Copy-Item C:\Users\deept\Downloads\index.html C:\Users\deept\deepthakkar\portfolio.html -Force`

- [ ] **Step 2: Add portfolio.html to builds in vercel.json**
  Modify: `C:\Users\deept\deepthakkar\vercel.json:11-13`
  Find:
  ```json
      {
        "src": "index.html",
        "use": "@vercel/static"
      }
  ```
  Replace with:
  ```json
      {
        "src": "index.html",
        "use": "@vercel/static"
      },
      {
        "src": "portfolio.html",
        "use": "@vercel/static"
      }
  ```

- [ ] **Step 3: Add route mapping in vercel.json**
  Modify: `C:\Users\deept\deepthakkar\vercel.json:46-49`
  Find:
  ```json
      {
        "src": "/github-repo-manager/(.*)",
        "dest": "api/proxy.js"
      },
      {
        "src": "/(.*)",
        "dest": "/$1"
      }
  ```
  Replace with:
  ```json
      {
        "src": "/github-repo-manager/(.*)",
        "dest": "api/proxy.js"
      },
      {
        "src": "/portfolio",
        "dest": "/portfolio.html"
      },
      {
        "src": "/(.*)",
        "dest": "/$1"
      }
  ```

- [ ] **Step 4: Verify vercel.json formatting**
  Verify the file syntax is correct JSON.

---

### Task 2: Deploy to Vercel

**Files:**
*   None.

**Interfaces:**
*   Consumes: Configured files from Task 1.
*   Produces: Deployed production link.

- [ ] **Step 1: Run Vercel production deployment**
  Run command: `npx vercel --prod` inside `C:\Users\deept\deepthakkar`
