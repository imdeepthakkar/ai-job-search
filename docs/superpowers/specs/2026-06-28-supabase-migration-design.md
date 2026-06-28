# Supabase Job Search Database Migration Design

**Date:** 2026-06-28  
**Status:** Approved  
**Topic:** Migrating from flat JSON/JS files in Git to a Supabase PostgreSQL database.

---

## 1. Objectives
- Eliminate Git commit/push cycle in GitHub Actions (preventing merge conflicts and sync failures).
- Implement real-time, bidirectional interactivity in the dashboard (marking jobs as read, applied, or ignored directly from the UI).
- Support rich, dynamic UI filters (date ranges, read/unread status, fit levels, tech stack tags, and application pipeline states).
- Migrate all historical scrape datasets from `job_scraper/data/` into the new Postgres database.

---

## 2. Architecture & Data Flow

```mermaid
graph TD
    subgraph GitHub Action (Daily)
        A[Run Scrapers] --> B[Gemini Fit Analysis]
        B --> C[run upload_history.py / publish.py]
    end

    C -->|Upsert via Service Key| D[(Supabase Postgres DB)]

    subgraph Vercel Frontend (Dashboard)
        E[User opens App] -->|Fetch via Anon Key| D
        F[Mark Applied / Read] -->|Write via RLS / Anon Key| D
    end
```

---

## 3. Database Schema

### Table: `jobs`

| Column Name | Data Type | Constraints / Default | Description |
| :--- | :--- | :--- | :--- |
| **`id`** | `TEXT` | `PRIMARY KEY` | Unique identifier (e.g., slugified `company-title` or platform ID). |
| **`title`** | `TEXT` | `NOT NULL` | The job title. |
| **`company`** | `TEXT` | `NOT NULL` | Company offering the position. |
| **`location`** | `TEXT` | | Location/region (e.g., `Greater Copenhagen`). |
| **`url`** | `TEXT` | `NOT NULL` | Direct link to the job posting. |
| **`fit`** | `TEXT` | `DEFAULT 'low'` | Fit assessment: `'high'`, `'medium'`, `'low'`. |
| **`status`** | `TEXT` | `DEFAULT 'new'` | Pipeline status: `'new'`, `'applied'`, `'interviewing'`, `'rejected'`, `'ignored'`. |
| **`is_read`** | `BOOLEAN` | `DEFAULT FALSE` | Tracker flag to show if you have viewed/clicked the job details. |
| **`first_seen`** | `DATE` | `DEFAULT CURRENT_DATE` | Date the job was first scraped. |
| **`last_seen`** | `DATE` | `DEFAULT CURRENT_DATE` | Latest date the job was confirmed active. |
| **`posted_date`**| `DATE` | | Actual date the job was published on the source site. |
| **`description`**| `TEXT` | | The job description text. |
| **`source`** | `TEXT` | | Source platform (e.g., `jobindex.dk`, `jobbank.dk`). |
| **`tags`** | `TEXT[]` | `DEFAULT '{}'` | Array of extracted tech/role keywords (e.g., `['azure', 'terraform', 'kubernetes']`). |
| **`notes`** | `TEXT` | | Personal notes about your application progress. |
| **`created_at`** | `TIMESTAMPTZ`| `DEFAULT now()` | Database record insertion time. |
| **`updated_at`** | `TIMESTAMPTZ`| `DEFAULT now()` | Database record last-modified time. |

---

## 4. Implementation Steps

### Step 4.1: Database Initialization
1. Create the `jobs` table using SQL DDL in the Supabase SQL editor.
2. Enable Row Level Security (RLS) on the `jobs` table if necessary, or configure policies allowing public reads and public/authenticated writes depending on security preference. (For convenience in a personal tracker, we can allow public select and update on the table).

### Step 4.2: Historical Data Migration
1. Write a script `job_scraper/upload_history.py`.
2. Load all historical JSON files from `job_scraper/data/*.json`.
3. Extract unique jobs across all files. For each job:
   - Identify `first_seen` (the earliest date of the files it appeared in).
   - Identify `last_seen` (the latest date of the files it appeared in).
4. Perform bulk upsert requests to Supabase to insert all historical jobs.

### Step 4.3: Daily Scraper Script Update
1. Update/rewrite the scrape publication script to fetch the latest scraped results and upsert them to Supabase (setting `last_seen = CURRENT_DATE` for active listings).
2. Decommission Git committing and pushing steps for static data files in `.github/workflows/gemini-daily-scrape.yml`.

### Step 4.4: Frontend Dashboard Updates
1. Replace static file loads with Supabase JS client client-side initialization.
2. Fetch job listings using Supabase SDK filters.
3. Build the UI filter controls:
   - **Date Range Slider/Pickers** using `first_seen` range.
   - **View state:** Seen (Read) vs. Not Seen (Unread).
   - **Application pipeline status:** Applied vs. Not Applied (New).
   - **Fit level:** High / Medium / Low.
4. Implement action handlers (e.g. click to toggle `is_read`, button to set status to `applied` or `ignored`).
