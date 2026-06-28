# Supabase Job Search Database Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the job scraper application from static JSON/JS files to a Supabase database, and upgrade the Vercel dashboard to use dynamic, real-time client-side queries and advanced UI filters.

**Architecture:** Use Supabase REST API (PostgREST) via lightweight Python `requests` calls for daily scraper upserts and historical migration. In the frontend, initialize the official `@supabase/supabase-js` client library via CDN to fetch and update jobs directly from the browser.

**Tech Stack:** Supabase (Postgres), HTML, Vanilla JavaScript, Python (requests, json, re), GitHub Actions.

## Global Constraints
- Target database: Supabase PostgreSQL
- File paths must match workspace directory structure
- No manual push or git commit steps of data files in the Daily Scrape workflow
- Ensure zero-dependency Python script where possible (using built-in libs or standard `requests`)

---

### Task 1: SQL Database Setup

**Files:**
- Create: `docs/superpowers/specs/db_schema.sql`

**Interfaces:**
- Produces: `jobs` table schema in Supabase Postgres.

- [ ] **Step 1: Write SQL Schema DDL**
  Create the SQL script at `docs/superpowers/specs/db_schema.sql` to define the table and indexes.
  ```sql
  -- Create jobs table
  CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      company TEXT NOT NULL,
      location TEXT,
      url TEXT NOT NULL,
      fit TEXT DEFAULT 'low' CHECK (fit IN ('high', 'medium', 'low')),
      status TEXT DEFAULT 'new' CHECK (status IN ('new', 'applied', 'interviewing', 'rejected', 'ignored')),
      is_read BOOLEAN DEFAULT FALSE,
      first_seen DATE DEFAULT CURRENT_DATE,
      last_seen DATE DEFAULT CURRENT_DATE,
      posted_date DATE,
      description TEXT,
      source TEXT,
      tags TEXT[] DEFAULT '{}',
      notes TEXT,
      created_at TIMESTAMPTZ DEFAULT now(),
      updated_at TIMESTAMPTZ DEFAULT now()
  );

  -- Index for fast status/fit querying and date filtering
  CREATE INDEX IF NOT EXISTS idx_jobs_status_fit ON jobs(status, fit);
  CREATE INDEX IF NOT EXISTS idx_jobs_last_seen ON jobs(last_seen);
  ```

- [ ] **Step 2: Commit DDL script**
  ```bash
  git add docs/superpowers/specs/db_schema.sql
  git commit -m "chore: add db schema DDL for Supabase setup"
  ```

- [ ] **Step 3: User instructions for Supabase Editor**
  Provide SQL DDL text to the user to execute in the Supabase SQL editor dashboard.

---

### Task 2: Write and Execute Historical Data Upload Script

**Files:**
- Create: `job_scraper/upload_history.py`

**Interfaces:**
- Consumes: JSON data files in `job_scraper/data/` and `job_scraper/seen_jobs.json`.
- Produces: Rows inserted/upserted into the Supabase database.

- [ ] **Step 1: Write upload script**
  Create [upload_history.py](file:///C:/Users/deept/ai-job-search/job_scraper/upload_history.py) to read all `.json` files in `job_scraper/data/`, resolve `first_seen` and `last_seen` dates, cross-reference `seen_jobs.json` for status/fit values, and bulk upload them to Supabase via POST.
  ```python
  import os
  import glob
  import json
  import re
  import requests
  from datetime import datetime

  WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  DATA_DIR = os.path.join(WORKSPACE_DIR, "job_scraper", "data")
  SEEN_JOBS_PATH = os.path.join(WORKSPACE_DIR, "job_scraper", "seen_jobs.json")

  SUPABASE_URL = os.environ.get("SUPABASE_URL")
  SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

  def upload():
      if not SUPABASE_URL or not SUPABASE_KEY:
          print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in env.")
          return

      # 1. Load seen_jobs.json status mapping
      seen_data = {}
      if os.path.exists(SEEN_JOBS_PATH):
          with open(SEEN_JOBS_PATH, "r", encoding="utf-8") as f:
              raw = json.load(f)
              seen_data = raw.get("seen", {})

      # 2. Gather historical data from all json files
      json_files = glob.glob(os.path.join(DATA_DIR, "2026-*.json"))
      
      all_jobs = {}
      for file_path in json_files:
          filename = os.path.basename(file_path)
          file_date = re.search(r"(\d{4}-\d{2}-\d{2})", filename).group(1)
          
          with open(file_path, "r", encoding="utf-8") as f:
              try:
                  jobs_list = json.load(f)
                  for job in jobs_list:
                      key = job.get("key")
                      if not key:
                          continue
                      
                      # Re-evaluate dates based on files they appeared in
                      if key not in all_jobs:
                          all_jobs[key] = {
                              "id": key,
                              "title": job.get("title"),
                              "company": job.get("company"),
                              "location": job.get("location"),
                              "url": job.get("url"),
                              "fit": job.get("fit", "low"),
                              "status": job.get("status", "new"),
                              "is_read": False,
                              "first_seen": file_date,
                              "last_seen": file_date,
                              "posted_date": job.get("date") if job.get("date") != "Recent" else None,
                              "description": job.get("description"),
                              "source": job.get("source"),
                              "tags": job.get("tags", []),
                              "notes": job.get("notes")
                          }
                      else:
                          # Update last_seen if this file is newer
                          if file_date > all_jobs[key]["last_seen"]:
                              all_jobs[key]["last_seen"] = file_date
                          # Update first_seen if this file is older
                          if file_date < all_jobs[key]["first_seen"]:
                              all_jobs[key]["first_seen"] = file_date
              except Exception as e:
                  print(f"Skipping {filename} due to parse error: {e}")

      # Apply seen_jobs overrides
      for key, job in all_jobs.items():
          if key in seen_data:
              job["status"] = seen_data[key].get("status", job["status"])
              job["fit"] = seen_data[key].get("fit", job["fit"])

      payload = list(all_jobs.values())
      print(f"Found {len(payload)} unique historical jobs to upload.")

      # 3. Post to Supabase REST endpoint
      url = f"{SUPABASE_URL}/rest/v1/jobs"
      headers = {
          "apikey": SUPABASE_KEY,
          "Authorization": f"Bearer {SUPABASE_KEY}",
          "Content-Type": "application/json",
          "Prefer": "resolution=merge-duplicates"
      }
      
      # Chunk size of 100 to prevent payloads being too large
      chunk_size = 100
      for i in range(0, len(payload), chunk_size):
          chunk = payload[i:i+chunk_size]
          response = requests.post(url, headers=headers, json=chunk)
          if response.status_code in [200, 201]:
              print(f"Successfully uploaded chunk {i // chunk_size + 1}/{len(payload) // chunk_size + 1}")
          else:
              print(f"Error uploading chunk {i // chunk_size + 1}: {response.text}")

  if __name__ == "__main__":
      upload()
  ```

- [ ] **Step 2: Commit upload script**
  ```bash
  git add job_scraper/upload_history.py
  git commit -m "feat: add script to upload historical jobs to Supabase"
  ```

---

### Task 3: Update Scraper Pipeline Script

**Files:**
- Modify: `job_scraper/export_all_jobs.py`

**Interfaces:**
- Consumes: Scraped search results, `SUPABASE_URL`, and `SUPABASE_SERVICE_KEY` env variables.
- Produces: Scraped jobs upserted to Supabase database.

- [ ] **Step 1: Refactor export_all_jobs.py**
  Replace local file writing commands with an upsert request directly to Supabase.
  Open [export_all_jobs.py](file:///C:/Users/deept/ai-job-search/job_scraper/export_all_jobs.py) and change the final execution section.
  Replace lines 231 to 296 with:
  ```python
      # 4. Upload to Supabase instead of saving files
      supabase_url = os.environ.get("SUPABASE_URL")
      supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
      
      if not supabase_url or not supabase_key:
          print("Warning: Supabase credentials missing from environment. Saving to local files as fallback.")
          # Fallback to saving date-specific files locally (pre-existing behavior)
          ...
          return
          
      payload = []
      for job in jobs_list:
          payload.append({
              "id": job["key"],
              "title": job["title"],
              "company": job["company"],
              "location": job["location"],
              "url": job["url"],
              "fit": job["fit"],
              "status": job["status"],
              "last_seen": date_str,
              "posted_date": job["date"] if job["date"] != "Recent" else None,
              "description": job["description"],
              "source": job["source"]
          })
          
      url = f"{supabase_url}/rest/v1/jobs"
      headers = {
          "apikey": supabase_key,
          "Authorization": f"Bearer {supabase_key}",
          "Content-Type": "application/json",
          "Prefer": "resolution=merge-duplicates"
      }
      
      response = requests.post(url, headers=headers, json=payload)
      if response.status_code in [200, 201]:
          print(f"Successfully upserted {len(payload)} active jobs to Supabase.")
      else:
          print(f"Error publishing to Supabase: {response.text}")
  ```

- [ ] **Step 2: Commit refactored script**
  ```bash
  git add job_scraper/export_all_jobs.py
  git commit -m "refactor: publish daily scraped jobs directly to Supabase"
  ```

---

### Task 4: GitHub Action Workflow Configuration

**Files:**
- Modify: `.github/workflows/gemini-daily-scrape.yml`

**Interfaces:**
- Consumes: Repository secrets `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`.

- [ ] **Step 1: Inject secrets and drop Git push step for data files**
  Open [.github/workflows/gemini-daily-scrape.yml](file:///C:/Users/deept/ai-job-search/.github/workflows/gemini-daily-scrape.yml).
  Inject environment variables `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in the step executing `export_all_jobs.py` (lines 169-171).
  ```yaml
        - name: 'Compile Dashboard Data'
          env:
            SUPABASE_URL: '${{ secrets.SUPABASE_URL }}'
            SUPABASE_SERVICE_KEY: '${{ secrets.SUPABASE_SERVICE_KEY }}'
          run: |-
            python job_scraper/export_all_jobs.py
  ```
  Modify the `Commit and Push Scrape Data` step (lines 173-186) to only commit/push `seen_jobs.json` or config files (and prevent pushing `data/*` files).
  Remove the `data/` push lines:
  ```bash
            # Remove data folder addition
            # git add job_scraper/data/*
  ```

- [ ] **Step 2: Commit workflow changes**
  ```bash
  git add .github/workflows/gemini-daily-scrape.yml
  git commit -m "ci: update Daily Job Scrape workflow for Supabase integration"
  ```

---

### Task 5: Upgrade Vercel Frontend UI (index.html)

**Files:**
- Modify: `job_scraper/index.html`

**Interfaces:**
- Consumes: Supabase JS library via CDN, environment variables injected at runtime or hardcoded keys securely matching anonymous scopes.
- Produces: Dynamic filter views, read status, and status updating in the database.

- [ ] **Step 1: Include Supabase CDN and initialize client**
  Open [index.html](file:///C:/Users/deept/ai-job-search/job_scraper/index.html).
  Add CDN in head:
  ```html
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
  ```
  Replace static date files loading in body script. Define Supabase client credentials and dynamic initialization:
  ```javascript
  const SUPABASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:54321' : 'https://your-project.supabase.co'; // Fallback or injected
  const SUPABASE_ANON_KEY = 'your-anon-key'; // Replace with public anon key
  
  const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  ```

- [ ] **Step 2: Update fetch logic in initApp() and loadJobData()**
  Rewrite `loadJobData` to query database rather than loading local JS files.
  ```javascript
  async function fetchSupabaseJobs() {
      const { data, error } = await supabase
          .from('jobs')
          .select('*')
          .gte('last_seen', new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]); // Active in last 14 days
          
      if (error) {
          console.error("Error fetching jobs:", error);
          throw error;
      }
      jobs = data;
  }
  ```

- [ ] **Step 3: Implement Database Sync for Actions**
  Update `toggleApplied` (lines 591-607) and `dismissJob` (lines 609-615) to perform Supabase DB updates:
  ```javascript
  async function toggleApplied(key) {
      const job = jobs.find(j => j.id === key);
      if (!job) return;
      const newStatus = job.status === 'applied' ? 'new' : 'applied';
      
      const { error } = await supabase
          .from('jobs')
          .update({ status: newStatus })
          .eq('id', key);
          
      if (!error) {
          job.status = newStatus;
          render();
          showToast(`Status updated successfully.`);
      }
  }
  ```

- [ ] **Step 4: Commit frontend changes**
  ```bash
  git add job_scraper/index.html
  git commit -m "feat: integrate Supabase client and database updates in dashboard frontend"
  ```
