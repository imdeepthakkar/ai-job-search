# Task 5 Report: Upgrade Vercel Frontend UI & Supabase Live Sync (Updated with Review Fixes)

## Implementation Summary
Upgraded the job search tool to support direct client-side integration with Supabase, dynamic credentials fallback via LocalStorage, dynamic Seen/Unseen read status tracking, and robust backend synchronization.

The following changes and code review fixes were implemented across the workspace:

### 1. Database Schema (`docs/superpowers/specs/db_schema.sql`)
- Appended a statement to disable Row Level Security (RLS) on the `jobs` table:
  ```sql
  ALTER TABLE jobs DISABLE ROW LEVEL SECURITY;
  ```
  This ensures that client-side SELECT/UPDATE operations initiated from the Vercel frontend in newly spawned Supabase projects are not blocked by default RLS policies.

### 2. Backend Scraper Sync (`job_scraper/export_all_jobs.py`)
- Created helper function `fetch_existing_jobs_from_supabase(supabase_url, supabase_key)` to retrieve all existing job IDs along with their current `status` and `fit` fields via the Supabase REST API (`GET /rest/v1/jobs?select=id,status,fit`).
- Updated the pipeline in `main()` to query the Supabase database before executing the upsert.
- When generating the upsert payload for newly scraped jobs, the script checks if the job already exists in the database. If it does, it overrides the scraper's default assessment with the values from the database, preserving the user's manual adjustments (e.g. keeping user-set `fit` or `status` values like `applied` or `ignored` instead of reverting them to `new`/`low`).
- Added error handling to the Supabase POST request: if the response status code is not 200 or 201, it logs the error output and exits the script using `sys.exit(1)`, ensuring CI/CD daily action run steps fail cleanly on database sync errors.

### 3. Frontend Dashboard (`job_scraper/index.html` & `job_scraper/index.css`)
- **Script Cleanups**: Removed the unused `<script src="data/dates.js"></script>` from `<head>`.
- **Dynamic Supabase Initialization**:
  - Re-implemented the Supabase client initialization. If the default hardcoded placeholder values (`'https://your-project.supabase.co'` and `'your-anon-key'`) are present, the client looks for `supabase_url` and `supabase_anon_key` inside `localStorage`.
  - Updated the Authentication screen: if valid Supabase credentials are not found in the placeholders or `localStorage`, the form dynamically reveals two extra inputs: "Supabase Project URL" and "Supabase Anon Key".
  - On successful login with developer account details (`deep@jobsearch.ai`/`Password123`), the custom credentials are saved to `localStorage`, and the page is reloaded automatically to instantiate the Supabase client.
- **Read Status & Seen Tracking (`is_read`)**:
  - Added a "Seen / Unseen Status" filter category in the sidebar (Unread and Read checkboxes) and registered them in the filters list and the filter-reset handler.
  - Redesigned card expansion tracking. Implemented `expandedKeys` (Set) to preserve which cards are open across screen updates, and refactored `toggleCardExpand(key)` to mark unread jobs (`is_read === false`) as read (`is_read = true`), trigger a re-render, and update the state in Supabase (`supabase.from('jobs').update({ is_read: true }).eq('id', key)`).
  - Implemented visual indicators for unread listings: added a `.unread-dot` class style in `index.css` (a glowing sky blue indicator dot) and updated `render()` to append this dot immediately before the title on cards where `is_read` is false.

### 4. CI/CD Workflow (`.github/workflows/gemini-daily-scrape.yml`)
- Inserted a preprocessing step in the `'Deploy to Vercel'` job immediately before installing and calling `vercel`.
- The new step runs `sed` inline replacement commands to swap out the hardcoded placeholders in `job_scraper/index.html` with the repository's secrets:
  ```bash
  sed -i "s|https://your-project.supabase.co|${{ secrets.SUPABASE_URL }}|g" job_scraper/index.html
  sed -i "s|your-anon-key|${{ secrets.SUPABASE_ANON_KEY }}|g" job_scraper/index.html
  ```

## Verification & Testing
1. **Python Syntax Compilation Check**: Passed validation successfully:
   ```bash
   python -m py_compile job_scraper/export_all_jobs.py
   ```
2. **HTML/JS Client Flow**: Checked elements definition, event listeners, variables, and logic. They align cleanly.
3. **CSS Class Verification**: Added `.unread-dot` class successfully to style definitions.

## Commits Created
- `9653bd6` - feat: integrate Supabase client and database updates in dashboard frontend
- `a28185c` - chore: apply final code review fixes for Supabase client, seen tracking, and CI/CD workflow
