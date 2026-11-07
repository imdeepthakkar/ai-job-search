#!/usr/bin/env python3
"""
notion_sync.py - Sync ranked jobs and tracker applications to Notion database.
Implements the specification in .claude/commands/notion-sync.md.
"""

import csv
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

def load_env_token():
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_KEY")
    if token:
        return token
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(root_dir, ".env")
    if os.path.isfile(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() in ("NOTION_TOKEN", "NOTION_API_KEY", "NOTION_KEY", "NOTION_SECRET"):
                            return v.strip().strip('"').strip("'")
        except Exception:
            pass
    return None

NOTION_TOKEN = load_env_token()
NOTION_VERSION = "2022-06-28"
NOTION_SYNC_FILE = os.path.join(os.path.dirname(__file__), "notion_sync.json")
SEEN_JOBS_FILE = os.path.join(os.path.dirname(__file__), "seen_jobs.json")
TRACKER_CSV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "job_search_tracker.csv")

def notion_api(endpoint, method="GET", payload=None):
    if not NOTION_TOKEN:
        print("Error: NOTION_TOKEN not found in environment or .env file.", file=sys.stderr)
        sys.exit(1)
    url = f"https://api.notion.com/v1/{endpoint}"
    data = json.dumps(payload).encode() if payload else None
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode()
        print(f"Notion API Error ({e.code}) on {endpoint}: {err_msg}", file=sys.stderr)
        raise

def normalize_status(raw_status):
    if not raw_status:
        return "applied"
    s = raw_status.strip().lower().replace(" ", "_")
    valid_statuses = [
        "ranked", "drafted", "applied", "interview", "offer",
        "hired", "rejected", "no_response", "offer_declined",
        "withdrawn", "expired"
    ]
    if s in valid_statuses:
        return s
    return "applied"

def load_sync_data(min_score=60, sync_all=False):
    sync_set = {}

    # 1. Load seen_jobs.json
    seen_jobs = {}
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
                seen_jobs = json.load(f)
        except Exception as e:
            print(f"Warning: Could not read {SEEN_JOBS_FILE}: {e}")

    for key, job in seen_jobs.items():
        status = job.get("status", "")
        score = job.get("rank_score", 0) or 0
        if status == "ranked" and (sync_all or score >= min_score):
            sync_set[key] = {
                "key": key,
                "role": job.get("title") or job.get("role", "Unknown Role"),
                "company": job.get("company", "Unknown Company"),
                "score": score,
                "verdict": job.get("rank_verdict", "Good Fit"),
                "status": "ranked",
                "fit": (job.get("fit") or "medium").lower(),
                "deadline": job.get("deadline"),
                "first_seen": job.get("first_seen"),
                "ranked_date": job.get("rank_date"),
                "applied_on": None,
                "channel": None,
                "cv_file": None,
                "cover_letter_file": None,
                "url": job.get("url"),
                "notes": job.get("notes"),
                "from_tracker": False
            }

    # 2. Load job_search_tracker.csv (Tracker always wins per spec!)
    if os.path.exists(TRACKER_CSV_FILE):
        try:
            with open(TRACKER_CSV_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    company = (row.get("company") or "").strip()
                    role = (row.get("role") or "").strip()
                    if not company and not role:
                        continue
                    
                    key = f"{company.lower()}_{role.lower()}".replace(" ", "_")
                    key = re.sub(r'[^a-z0-9_]', '', key)
                    
                    target_key = key
                    for k in sync_set:
                        if k.lower() == key.lower():
                            target_key = k
                            break
                    
                    status = normalize_status(row.get("status"))
                    fit_str = (row.get("fit_rating") or "Medium").lower()
                    fit = "high" if "high" in fit_str else ("low" if "low" in fit_str else "medium")
                    
                    sync_set[target_key] = {
                        "key": target_key,
                        "role": role,
                        "company": company,
                        "score": sync_set.get(target_key, {}).get("score", 75),
                        "verdict": sync_set.get(target_key, {}).get("verdict", "Good Fit"),
                        "status": status,
                        "fit": fit,
                        "deadline": row.get("deadline") or sync_set.get(target_key, {}).get("deadline"),
                        "first_seen": sync_set.get(target_key, {}).get("first_seen") or row.get("date"),
                        "ranked_date": sync_set.get(target_key, {}).get("ranked_date"),
                        "applied_on": row.get("date") if status != "drafted" else None,
                        "channel": (row.get("channel") or "portal").lower(),
                        "cv_file": row.get("cv_file"),
                        "cover_letter_file": row.get("cover_letter_file"),
                        "url": row.get("source") or sync_set.get(target_key, {}).get("url"),
                        "notes": row.get("notes"),
                        "from_tracker": True
                    }
        except Exception as e:
            print(f"Warning: Could not read {TRACKER_CSV_FILE}: {e}")

    return sync_set

def query_existing_pages(database_id):
    pages_by_key = {}
    has_more = True
    start_cursor = None
    while has_more:
        body = {"page_size": 100}
        if start_cursor:
            body["start_cursor"] = start_cursor
        res = notion_api(f"databases/{database_id}/query", method="POST", payload=body)
        for page in res.get("results", []):
            props = page.get("properties", {})
            key_items = props.get("Key", {}).get("rich_text", [])
            if key_items:
                k = key_items[0].get("plain_text")
                pages_by_key[k] = page["id"]
        has_more = res.get("has_more", False)
        start_cursor = res.get("next_cursor")
    return pages_by_key

def sync():
    if not os.path.exists(NOTION_SYNC_FILE):
        print("Error: notion_sync.json not found.")
        sys.exit(1)

    with open(NOTION_SYNC_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    db_id = cfg["database_id"]
    db_url = cfg["database_url"]

    sync_set = load_sync_data()
    print(f"Sync set: {len(sync_set)} jobs/applications.")
    existing_pages = query_existing_pages(db_id)
    print(f"Already in database: {len(existing_pages)}")

    created = 0
    updated = 0

    for key, item in sync_set.items():
        title_str = f"{item['role']} — {item['company']}"
        props = {
            "Name": {"title": [{"text": {"content": title_str}}]},
            "Company": {"rich_text": [{"text": {"content": item["company"]}}]},
            "Key": {"rich_text": [{"text": {"content": item["key"]}}]},
            "Status": {"select": {"name": item["status"]}},
            "Fit": {"select": {"name": item["fit"]}},
        }

        if item.get("score") is not None:
            props["Score"] = {"number": item["score"]}
        if item.get("verdict"):
            props["Verdict"] = {"select": {"name": item["verdict"]}}
        if item.get("channel"):
            props["Channel"] = {"select": {"name": item["channel"]}}
        if item.get("url") and item["url"].startswith("http"):
            props["URL"] = {"url": item["url"]}
        if item.get("cv_file"):
            props["CV file"] = {"rich_text": [{"text": {"content": item["cv_file"]}}]}
        if item.get("cover_letter_file"):
            props["Cover letter"] = {"rich_text": [{"text": {"content": item["cover_letter_file"]}}]}
        if item.get("applied_on") and re.match(r'^\d{4}-\d{2}-\d{2}$', str(item["applied_on"])):
            props["Applied on"] = {"date": {"start": str(item["applied_on"])}}
        if item.get("deadline") and re.match(r'^\d{4}-\d{2}-\d{2}$', str(item["deadline"])):
            props["Deadline"] = {"date": {"start": str(item["deadline"])}}
        if item.get("first_seen") and re.match(r'^\d{4}-\d{2}-\d{2}$', str(item["first_seen"])):
            props["First seen"] = {"date": {"start": str(item["first_seen"])}}
        if item.get("ranked_date") and re.match(r'^\d{4}-\d{2}-\d{2}$', str(item["ranked_date"])):
            props["Ranked"] = {"date": {"start": str(item["ranked_date"])}}

        if key in existing_pages:
            page_id = existing_pages[key]
            notion_api(f"pages/{page_id}", method="PATCH", payload={"properties": props})
            updated += 1
            print(f"  [*] Updated: {title_str}")
        else:
            children = [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"text": {"content": "Application Timeline & Notes"}}]}
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"text": {"content": f"Status: {item['status']} | Channel: {item.get('channel', 'N/A')} | Applied: {item.get('applied_on', 'N/A')}\n"}},
                            {"text": {"content": f"Notes: {item.get('notes') or 'No notes provided'}"}}
                        ]
                    }
                }
            ]
            if item.get("url") and item["url"].startswith("http"):
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"text": {"content": "Posting URL: "}},
                            {"text": {"content": item["url"], "link": {"url": item["url"]}}}
                        ]
                    }
                })

            body = {
                "parent": {"database_id": db_id},
                "properties": props,
                "children": children
            }
            notion_api("pages", method="POST", payload=body)
            created += 1
            print(f"  [+] Created: {title_str}")
        
        time.sleep(0.35)

    cfg["last_sync"] = datetime.now().strftime("%Y-%m-%d")
    with open(NOTION_SYNC_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    print("\n-------------------------------------------")
    print(f"Sync complete! Created: {created}, Updated: {updated}")
    print(f"Database URL: {db_url}")
    print("-------------------------------------------")

if __name__ == "__main__":
    sync()
