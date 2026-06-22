#!/usr/bin/env python3
import os
import sys
import json
import csv
import re
import subprocess
from datetime import datetime, timedelta

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN_JOBS_PATH = os.path.join(WORKSPACE_DIR, "job_scraper", "seen_jobs.json")
TRACKER_PATH = os.path.join(WORKSPACE_DIR, "job_search_tracker.csv")
TARGET_REPORT_PATH = os.path.join(WORKSPACE_DIR, "targeted_scrape_report.md")

JOBINDEX_CLI_DIR = os.path.join(WORKSPACE_DIR, ".agents", "skills", "jobindex-search", "cli")
JOBBANK_CLI_DIR = os.path.join(WORKSPACE_DIR, ".agents", "skills", "jobbank-search", "cli")

def load_seen_jobs():
    if os.path.exists(SEEN_JOBS_PATH):
        try:
            with open(SEEN_JOBS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "seen" in data:
                    return data
        except Exception as e:
            print(f"Warning: Failed to load seen_jobs.json: {e}")
    return {"seen": {}}

def save_seen_jobs(seen_data):
    try:
        with open(SEEN_JOBS_PATH, "w", encoding="utf-8") as f:
            json.dump(seen_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error: Failed to save seen_jobs.json: {e}")

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

def run_jobindex_search(query):
    # Appending København to make search targeted on Jobindex
    search_q = f'"{query}" københavn'
    print(f"Running Jobindex search for: '{search_q}'...")
    try:
        cmd = ["bun", "run", "src/cli.ts", "search", "--query", search_q, "--jobage", "14", "--format", "json"]
        result = subprocess.run(cmd, cwd=JOBINDEX_CLI_DIR, capture_output=True, text=True, check=True, encoding="utf-8")
        data = json.loads(result.stdout)
        return data.get("results", [])
    except Exception as e:
        print(f"Error running Jobindex search for '{search_q}': {e}")
        return []

def run_jobbank_search(query):
    # Location 2 is Storkøbenhavn
    print(f"Running Jobbank search for key: '{query}' in Storkøbenhavn...")
    try:
        cmd = ["bun", "run", "src/cli.ts", "search", "--key", query, "--location", "2", "--format", "json"]
        result = subprocess.run(cmd, cwd=JOBBANK_CLI_DIR, capture_output=True, text=True, check=True, encoding="utf-8")
        data = json.loads(result.stdout)
        return data.get("results", [])
    except Exception as e:
        print(f"Error running Jobbank search for '{query}': {e}")
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

def is_location_ok(location):
    if not location:
        return True
    loc_lower = location.lower()
    
    ideal_locs = ["copenhagen", "københavn", "storkøbenhavn", "greater copenhagen", "frederiksberg", "hellerup", "glostrup", "ballerup", "kastrup", "herlev", "lyngby", "søborg", "brøndby", "hvidovre", "rødovre", "taastrup", "tåstrup"]
    acceptable_locs = ["roskilde", "hillerød", "køge", "remote", "hybrid", "hjemmearbejde"]
    
    return any(i in loc_lower for i in ideal_locs + acceptable_locs)

def assess_fit(title, company, description):
    title_lower = title.lower()
    desc_lower = (description or "").lower()
    comp_lower = (company or "").lower()
    
    non_target_terms = ["junior", "student", "intern", "sales", "hr", "recruiter", "marketing", "pricing"]
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
    print("[START] Starting targeted job scraper...")
    
    # 1. Load State
    seen_jobs = load_seen_jobs()
    applied_jobs = load_applied_jobs()
    
    target_roles = ["Senior Software Engineer", "Technical Lead", "Lead", "Solution Architect"]
    
    raw_results = []
    
    # 2. Run Searches
    for role in target_roles:
        # Run Jobindex
        jobindex_res = run_jobindex_search(role)
        for r in jobindex_res:
            r['source_site'] = 'jobindex.dk'
            raw_results.append(r)
            
        # Run Jobbank
        jobbank_res = run_jobbank_search(role)
        for r in jobbank_res:
            r['source_site'] = 'jobbank.dk'
            raw_results.append(r)
            
    print(f"\nFetched {len(raw_results)} raw postings before filtering.")
    
    # 3. Process & Deduplicate
    unique_jobs = {}
    cutoff_date = datetime.now() - timedelta(days=14)
    
    for job in raw_results:
        title = job.get('title')
        company = job.get('company')
        url = job.get('url')
        
        if not title or not url:
            continue
            
        # Filter: Title must align with requested technical/engineering roles
        title_lower = title.lower()
        valid_title = any(term.lower() in title_lower for term in ["software", "developer", "architect", "lead", "engineer", "udvikler"])
        if not valid_title:
            continue
            
        key = make_key(company, title)
        if key in unique_jobs:
            if len(unique_jobs[key].get('description') or '') < len(job.get('description') or ''):
                unique_jobs[key] = job
            continue
            
        unique_jobs[key] = job
        
    print(f"Deduplicated to {len(unique_jobs)} unique target listings.")
    
    # Filter and categorize
    new_matches = []
    skipped_count = 0
    
    for key, job in unique_jobs.items():
        title = job.get('title')
        company = job.get('company', 'Unknown Company') or 'Unknown Company'
        url = job.get('url')
        location = job.get('location', '')
        date_str = job.get('date') or job.get('posted')
        description = job.get('description', '')
        
        tracker_key = f"{company.strip().lower()}|{title.strip().lower()}"
        if tracker_key in applied_jobs:
            skipped_count += 1
            if key in seen_jobs['seen']:
                seen_jobs['seen'][key]['status'] = 'applied'
            continue
            
        is_already_seen = key in seen_jobs['seen']
        
        job_date = parse_date(date_str)
        if job_date and job_date < cutoff_date:
            continue
            
        if not is_location_ok(location):
            continue
            
        fit = assess_fit(title, company, description)
        
        seen_metadata = {
            "title": title,
            "company": company,
            "url": url,
            "first_seen": datetime.now().strftime("%Y-%m-%d"),
            "fit": fit,
            "status": "applied" if tracker_key in applied_jobs else ("new" if not is_already_seen else seen_jobs['seen'][key].get('status', 'new'))
        }
        
        seen_jobs['seen'][key] = seen_metadata
        
        # We present all matches in the targeted report, but highlight if it's new vs seen
        new_matches.append({
            "key": key,
            "title": title,
            "company": company,
            "location": location or "Storkøbenhavn",
            "url": url,
            "fit": fit,
            "date": job_date.strftime("%Y-%m-%d") if job_date else "Recent",
            "description": description,
            "is_new": not is_already_seen
        })
        
    save_seen_jobs(seen_data=seen_jobs)
    
    fit_priority = {"high": 0, "medium": 1, "low": 2}
    new_matches.sort(key=lambda x: fit_priority.get(x['fit'], 2))
    
    high_matches = [m for m in new_matches if m['fit'] == 'high']
    medium_matches = [m for m in new_matches if m['fit'] == 'medium']
    low_matches = [m for m in new_matches if m['fit'] == 'low']
    
    print(f"\nProcessing complete:")
    print(f"  - Matches found: {len(new_matches)}")
    print(f"    - High match: {len(high_matches)}")
    print(f"    - Medium match: {len(medium_matches)}")
    print(f"    - Low match: {len(low_matches)}")
    
    # 4. Generate Report
    report_content = []
    report_content.append(f"# Targeted Job Scraper Report - {datetime.now().strftime('%Y-%m-%d')}\n")
    report_content.append(f"Found {len(new_matches)} positions matching: Senior Software Engineer, Technical Lead, Lead, and Solution Architect in Greater Copenhagen ({len(high_matches)} high, {len(medium_matches)} medium, {len(low_matches)} low match).\n")
    
    if new_matches:
        report_content.append("| # | Fit | New? | Title | Company | Location | Date | Link |")
        report_content.append("|---|-----|------|-------|---------|----------|------|------|")
        for idx, m in enumerate(new_matches, 1):
            fit_badge = f"**{m['fit'].upper()}**" if m['fit'] == 'high' else m['fit'].capitalize()
            new_badge = "Yes" if m['is_new'] else "No"
            report_content.append(f"| {idx} | {fit_badge} | {new_badge} | {m['title']} | {m['company']} | {m['location']} | {m['date']} | [Link]({m['url']}) |")
        
        report_content.append("\n## High-Match Highlights\n")
        if high_matches:
            for idx, m in enumerate(high_matches, 1):
                report_content.append(f"### {idx}. {m['title']} at {m['company']}")
                report_content.append(f"- **URL:** {m['url']}")
                report_content.append(f"- **Location:** {m['location']}")
                
                alignments = []
                title_lower = m['title'].lower()
                desc_lower = (m['description'] or "").lower()
                
                if "architect" in title_lower:
                    alignments.append("Direct solutions / system architecture role matching your Core Expertise")
                if "lead" in title_lower or "technical lead" in title_lower:
                    alignments.append("Technical leadership position aligned with your role at TCS Mastercard")
                if any(x in desc_lower or x in title_lower for x in ["azure", "cloud"]):
                    alignments.append("Requires cloud-native design & Azure infrastructure expertise")
                if "terraform" in desc_lower or "terraform" in title_lower:
                    alignments.append("Involves Infrastructure as Code (IaC) & automation")
                if any(x in desc_lower for x in ["payment", "banking", "finance", "fintech"]):
                    alignments.append("Leverages your finance/payments sector domain knowledge from Mastercard")
                if any(x in desc_lower for x in ["java", "spring"]):
                    alignments.append("Java/Spring Boot ecosystem alignment")
                    
                if not alignments:
                    alignments.append("Matches your overall senior technical background and capabilities")
                    
                report_content.append("- **Why it matches your profile:**")
                for align in alignments:
                    report_content.append(f"  - {align}")
                report_content.append("")
        else:
            report_content.append("No high-match positions found in this run.\n")
    else:
        report_content.append("No matching job postings found.\n")
        
    with open(TARGET_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))
        
    print(f"Report written to {TARGET_REPORT_PATH}")
    
    print("\n--- REPORT START ---")
    try:
        print("\n".join(report_content))
    except UnicodeEncodeError:
        print("\n".join(report_content).encode('ascii', errors='replace').decode('ascii'))
    print("--- REPORT END ---")

if __name__ == "__main__":
    main()
