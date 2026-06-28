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
