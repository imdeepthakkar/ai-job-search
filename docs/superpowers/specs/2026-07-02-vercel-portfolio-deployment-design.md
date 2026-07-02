# Design Spec: Vercel Portfolio Deployment

## Status
Approved

## Background & Goals
Deploy the newly updated portfolio site under the URL path `/portfolio` on the Vercel project `deepthakkar` (which serves `deepthakkar.vercel.app`).

## Requirements
*   Serve the detailed portfolio HTML file at `/portfolio`.
*   Ensure all links and routes in `vercel.json` are maintained.
*   Deploy using Vercel CLI.

## Design Details

### 1. File Copy
Copy the updated `index.html` from `C:\Users\deept\Downloads\index.html` to `C:\Users\deept\deepthakkar\portfolio.html`.

### 2. vercel.json Configuration

Modify `C:\Users\deept\deepthakkar\vercel.json` to include the build configuration and the route rule:

```json
{
  "version": 2,
  "name": "deepthakkar",
  "builds": [
    {
      "src": "api/proxy.js",
      "use": "@vercel/node"
    },
    {
      "src": "index.html",
      "use": "@vercel/static"
    },
    {
      "src": "portfolio.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/greencart",
      "dest": "api/proxy.js"
    },
    {
      "src": "/greencart/(.*)",
      "dest": "api/proxy.js"
    },
    {
      "src": "/luxtravel",
      "dest": "api/proxy.js"
    },
    {
      "src": "/luxtravel/(.*)",
      "dest": "api/proxy.js"
    },
    {
      "src": "/ai-job-search",
      "dest": "api/proxy.js"
    },
    {
      "src": "/ai-job-search/(.*)",
      "dest": "api/proxy.js"
    },
    {
      "src": "/github-repo-manager",
      "dest": "api/proxy.js"
    },
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
  ]
}
```

## Testing & Deployment Plan
1. Check syntax of `vercel.json`.
2. Run `npx vercel --prod` inside the `deepthakkar` folder to execute deployment.
3. Verify that `https://deepthakkar.vercel.app/portfolio` resolves correctly.
