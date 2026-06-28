import os
import glob
import json
import re
import requests
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORKSPACE_DIR, "job_scraper", "data")
SEEN_JOBS_PATH = os.path.join(WORKSPACE_DIR, "job_scraper", "seen_jobs.json")

def upload():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not supabase_key:
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
        # Try to find a date match in the filename
        match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
        if not match:
            continue
        file_date = match.group(1)
        
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
    url = f"{supabase_url}/rest/v1/jobs"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    # Chunk size of 100 to prevent payloads being too large
    chunk_size = 100
    for i in range(0, len(payload), chunk_size):
        chunk = payload[i:i+chunk_size]
        response = requests.post(url, headers=headers, json=chunk)
        if response.status_code in [200, 201]:
            print(f"Successfully uploaded chunk {i // chunk_size + 1}/{(len(payload) - 1) // chunk_size + 1}")
        else:
            print(f"Error uploading chunk {i // chunk_size + 1}: {response.status_code} - {response.text}")

if __name__ == "__main__":
    upload()
