#!/usr/bin/env python3
import os
import sys
import json
import csv
import re
import subprocess
from datetime import datetime, timedelta

WORKSPACE_DIR = r"C:\Users\deept\ai-job-search"
QUERIES_PATH = os.path.join(WORKSPACE_DIR, ".claude", "skills", "job-scraper", "search-queries.md")
TRACKER_PATH = os.path.join(WORKSPACE_DIR, "job_search_tracker.csv")
SEEN_JOBS_PATH = os.path.join(WORKSPACE_DIR, "job_scraper", "seen_jobs.json")

JOBINDEX_CLI_DIR = os.path.join(WORKSPACE_DIR, ".agents", "skills", "jobindex-search", "cli")
JOBBANK_CLI_DIR = os.path.join(WORKSPACE_DIR, ".agents", "skills", "jobbank-search", "cli")

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
            print(f"Warning: Failed to load job_search_tracker.csv: {e}")
    return applied

def load_seen_status():
    seen = {}
    if os.path.exists(SEEN_JOBS_PATH):
        try:
            with open(SEEN_JOBS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "seen" in data:
                    for k, v in data["seen"].items():
                        seen[k] = v.get("status", "new")
        except Exception as e:
            print(f"Warning: Failed to load seen_jobs.json: {e}")
    return seen

def parse_search_queries():
    default_titles = ["Solution Architect", "Technical Lead", "Senior Software Engineer", "DevOps Engineer"]
    if not os.path.exists(QUERIES_PATH):
        return default_titles
    try:
        with open(QUERIES_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        titles = set()
        title_matches = re.findall(r"-\s*\*\*Titles:\*\*\s*(.*)", content)
        for tm in title_matches:
            for title in tm.split(","):
                t = title.strip()
                if t:
                    titles.add(t)
        keyword_matches = re.findall(r"-\s*\*\*Keywords:\*\*\s*(.*)", content)
        keywords = set()
        for km in keyword_matches:
            for kw in km.split(","):
                k = kw.strip()
                if k:
                    keywords.add(k)
        search_terms = list(titles)
        if "Terraform" in keywords:
            search_terms.append("Terraform")
        if "DevSecOps" in keywords:
            search_terms.append("DevSecOps")
        search_terms = [s for s in search_terms if s.lower() not in ["lead", "architect"]]
        return sorted(list(set(search_terms)))
    except Exception as e:
        print(f"Error parsing search queries: {e}")
        return default_titles

def run_jobindex_search(query):
    try:
        cmd = ["bun", "run", "src/cli.ts", "search", "--query", query, "--jobage", "14", "--format", "json"]
        result = subprocess.run(cmd, cwd=JOBINDEX_CLI_DIR, capture_output=True, text=True, check=True, encoding="utf-8")
        data = json.loads(result.stdout)
        return data.get("results", [])
    except Exception as e:
        return []

def run_jobbank_search(query):
    try:
        cmd = ["bun", "run", "src/cli.ts", "search", "--key", query, "--location", "2", "--format", "json"]
        result = subprocess.run(cmd, cwd=JOBBANK_CLI_DIR, capture_output=True, text=True, check=True, encoding="utf-8")
        data = json.loads(result.stdout)
        return data.get("results", [])
    except Exception as e:
        return []

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass
    try:
        parts = date_str.split(",")
        if len(parts) > 1:
            date_part = parts[1].strip().split(" ")
            if len(date_part) >= 3:
                day, month_str, year = date_part[0], date_part[1], date_part[2]
                months = {
                    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
                }
                month = months.get(month_str[:3], 1)
                return datetime(int(year), month, int(day))
    except Exception:
        pass
    return None

def assess_fit(title, company, description):
    title_lower = title.lower()
    desc_lower = (description or "").lower()
    comp_lower = (company or "").lower()
    
    non_target_terms = ["junior", "student", "intern", "sales manager", "recruiter", "pricing analyst", "hr", "marketing manager"]
    if any(t in title_lower for t in non_target_terms):
        return "low"
        
    high_keywords = [
        "architect", "solution architect", "solutions architect", "technical lead", "tech lead", 
        "devops lead", "platform architect", "infrastructure architect", "principal architect", "cloud architect"
    ]
    
    tech_keywords = [
        "azure", "terraform", "java", "spring", "kubernetes", "microservices", "devops", 
        "payment", "mastercard", "fintech", "sre", "observability", "splunk", "dynatrace"
    ]
    
    is_architect_or_lead = any(k in title_lower for k in high_keywords)
    has_tech_match = any(t in title_lower or t in desc_lower for t in tech_keywords)
    
    fin_companies = ["mastercard", "nets", "danske bank", "nordea", "nykredit", "jyske bank", "simcorp", "saxo bank"]
    is_fin_match = any(fc in comp_lower for fc in fin_companies)
    
    if is_architect_or_lead and (has_tech_match or is_fin_match):
        return "high"
    elif is_architect_or_lead or (("senior" in title_lower or "lead" in title_lower or "principal" in title_lower) and has_tech_match):
        return "medium"
    else:
        return "low"

def slugify(text):
    text = text.lower()
    text = text.replace('æ', 'ae').replace('ø', 'oe').replace('å', 'aa')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def make_key(company, title):
    comp_slug = slugify(company or 'unknown')
    title_slug = slugify(title or 'unknown')
    return f"{comp_slug}-{title_slug}"[:60]

def main():
    print("Compiling all scraped jobs to JSON...")
    applied_jobs = load_applied_jobs()
    seen_status = load_seen_status()
    search_queries = parse_search_queries()
    
    raw_results = []
    for query in search_queries:
        # Jobindex
        for r in run_jobindex_search(query):
            r['source_site'] = 'jobindex.dk'
            raw_results.append(r)
        # Jobbank
        for r in run_jobbank_search(query):
            r['source_site'] = 'jobbank.dk'
            raw_results.append(r)
            
    # Deduplicate & Filter
    unique_jobs = {}
    cutoff_date = datetime.now() - timedelta(days=14)
    
    for job in raw_results:
        title = job.get('title')
        company = job.get('company')
        url = job.get('url')
        if not title or not url:
            continue
            
        key = make_key(company, title)
        if key in unique_jobs:
            if len(unique_jobs[key].get('description') or '') < len(job.get('description') or ''):
                unique_jobs[key] = job
            continue
        unique_jobs[key] = job

    jobs_list = []
    for key, job in unique_jobs.items():
        title = job.get('title')
        company = job.get('company', 'Unknown Company') or 'Unknown Company'
        url = job.get('url')
        location = job.get('location', 'Greater Copenhagen') or 'Greater Copenhagen'
        date_str = job.get('date') or job.get('posted')
        description = job.get('description', '')
        
        tracker_key = f"{company.strip().lower()}|{title.strip().lower()}"
        status = "applied" if tracker_key in applied_jobs else seen_status.get(key, "new")
        
        job_date = parse_date(date_str)
        if job_date and job_date < cutoff_date:
            continue
            
        fit = assess_fit(title, company, description)
        
        jobs_list.append({
            "key": key,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "fit": fit,
            "date": job_date.strftime("%Y-%m-%d") if job_date else "Recent",
            "description": description or "No description available.",
            "source": job.get('source_site', 'Unknown'),
            "status": status
        })
        
    jobs_list.sort(key=lambda x: ({"high": 0, "medium": 1, "low": 2}.get(x['fit'], 2), x['date']), reverse=False)
    
    # 4. Save date-specific files
    date_str = datetime.now().strftime("%Y-%m-%d")
    data_dir = os.path.join(WORKSPACE_DIR, "job_scraper", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    today_json_path = os.path.join(data_dir, f"{date_str}.json")
    today_js_path = os.path.join(data_dir, f"{date_str}.js")
    
    with open(today_json_path, "w", encoding="utf-8") as f:
        json.dump(jobs_list, f, indent=2, ensure_ascii=False)
        
    with open(today_js_path, "w", encoding="utf-8") as f:
        f.write(f"window.scrapedJobs = {json.dumps(jobs_list, indent=2, ensure_ascii=False)};")
        
    # Update dates registry
    dates_js_path = os.path.join(data_dir, "dates.js")
    available_dates = [date_str]
    if os.path.exists(dates_js_path):
        try:
            with open(dates_js_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"window\.availableDates\s*=\s*(\[.*?\]);", content, re.DOTALL)
                if match:
                    existing_dates = json.loads(match.group(1))
                    if isinstance(existing_dates, list):
                        available_dates = sorted(list(set(existing_dates + [date_str])), reverse=True)
        except Exception as e:
            print(f"Warning: Failed to parse dates.js: {e}")
            
    with open(dates_js_path, "w", encoding="utf-8") as f:
        f.write(f"window.availableDates = {json.dumps(available_dates, indent=2, ensure_ascii=False)};")
        
    print(f"Successfully exported {len(jobs_list)} unique jobs for {date_str}")
    print(f"Updated dates registry at {dates_js_path}")

if __name__ == "__main__":
    main()
