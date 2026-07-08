-- Migration to update the check constraint on jobs status in Supabase
ALTER TABLE jobs DROP CONSTRAINT IF EXISTS jobs_status_check;

ALTER TABLE jobs ADD CONSTRAINT jobs_status_check CHECK (
    status IN ('new', 'applied', 'interviewing', 'rejected', 'ignored', 'ranked', 'expired')
);
