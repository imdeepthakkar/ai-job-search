#!/usr/bin/env python3
import os
import json
import csv
import re

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKER_PATH = os.path.join(WORKSPACE_DIR, "job_search_tracker.csv")
SEEN_JOBS_PATH = os.path.join(WORKSPACE_DIR, "job_scraper", "seen_jobs.json")
INPUT_FILE = os.path.join(WORKSPACE_DIR, ".temp", "unique_results.json")

def slugify(text):
    if not text:
        return 'unknown'
    text = text.lower()
    text = text.replace('æ', 'ae').replace('ø', 'oe').replace('å', 'aa')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def make_key(company, title):
    comp_slug = slugify(company or 'unknown')
    title_slug = slugify(title or 'unknown')
    return f"{comp_slug}-{title_slug}"[:60]

def load_applied_jobs():
    applied = set()
    if os.path.exists(TRACKER_PATH):
        try:
            with open(TRACKER_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    company = row.get("company", "").strip().lower()
                    role = row.get("role", "").strip().lower()
                    if company and role:
                        applied.add(f"{company}|{role}")
        except Exception as e:
            print(f"Warning: Failed to load tracker: {e}")
    return applied

def load_seen_keys():
    seen_keys = set()
    if os.path.exists(SEEN_JOBS_PATH):
        try:
            with open(SEEN_JOBS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "seen" in data:
                    seen_keys = set(data["seen"].keys())
        except Exception as e:
            print(f"Warning: Failed to load seen_jobs: {e}")
    return seen_keys

def main():
    print("Filtering out already seen or applied jobs from input data...")
    if not os.path.exists(INPUT_FILE):
        print(f"Input file {INPUT_FILE} not found. Skipping.")
        return
        
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            jobs = json.load(f)
    except Exception as e:
        print(f"Error loading input file: {e}")
        return

    applied_jobs = load_applied_jobs()
    seen_keys = load_seen_keys()
    
    filtered_jobs = []
    skipped_seen = 0
    skipped_applied = 0
    
    for job in jobs:
        title = job.get('title')
        company = job.get('company', 'Unknown Company') or 'Unknown Company'
        
        # Check against applied tracker
        tracker_key = f"{company.strip().lower()}|{title.strip().lower()}"
        if tracker_key in applied_jobs:
            skipped_applied += 1
            continue
            
        # Check against seen database
        key = make_key(company, title)
        if key in seen_keys:
            skipped_seen += 1
            continue
            
        filtered_jobs.append(job)
        
    print(f"Original jobs: {len(jobs)}")
    print(f"Filtered out: {skipped_seen} already seen, {skipped_applied} already applied.")
    print(f"Remaining new jobs: {len(filtered_jobs)}")
    
    try:
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(filtered_jobs, f, indent=2, ensure_ascii=False)
        print(f"Updated {INPUT_FILE} with new jobs list.")
    except Exception as e:
        print(f"Error saving filtered jobs: {e}")

if __name__ == "__main__":
    main()
