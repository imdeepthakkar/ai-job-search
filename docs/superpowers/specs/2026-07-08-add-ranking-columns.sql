-- Migration to add ranking columns to jobs table
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS rank_score NUMERIC;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS rank_verdict TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS strengths TEXT[] DEFAULT '{}';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS gaps TEXT[] DEFAULT '{}';
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS rank_date DATE;

-- Create an index to quickly filter/sort by rank_score and rank_date
CREATE INDEX IF NOT EXISTS idx_jobs_rank_score ON jobs(rank_score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_rank_date ON jobs(rank_date DESC);
