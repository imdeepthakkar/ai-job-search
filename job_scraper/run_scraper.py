#!/usr/bin/env python3
import os
import sys
import json
import csv
import re
import subprocess
import yaml
import concurrent.futures
from datetime import datetime, timedelta

# Constants
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN_JOBS_PATH = os.path.join(WORKSPACE_DIR, "job_scraper", "seen_jobs.json")
TRACKER_PATH = os.path.join(WORKSPACE_DIR, "job_search_tracker.csv")
CONFIG_PATH = os.path.join(WORKSPACE_DIR, "job_scraper", "config.yaml")
REPORT_PATH = os.path.join(WORKSPACE_DIR, "scrape_report.md")

JOBINDEX_CLI_DIR = os.path.join(WORKSPACE_DIR, ".agents", "skills", "jobindex-search", "cli")
JOBBANK_CLI_DIR = os.path.join(WORKSPACE_DIR, ".agents", "skills", "jobbank-search", "cli")

CONFIG = {}

def load_config():
    global CONFIG
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                CONFIG = yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Failed to load config.yaml: {e}")
    else:
        print(f"Warning: config.yaml not found at {CONFIG_PATH}")

# Initialize config
load_config()

# Legal suffixes and noise to strip when matching company names
STRIP_PATTERNS = [
    r"\ba/s\b", r"\baps\b", r"\bi/s\b", r"\bp/s\b", r"\bk/s\b",
    r"\bivs\b", r"\bamba\b", r"\ba\.m\.b\.a\.\b",
    r"\(vg\)", r"\(.*?\)",  # (VG) and other parentheticals
    r"\bdanmark\b", r"\bdenmark\b", r"\bscandinavia\b", r"\bnordic\b",
    r"\bgroup\b", r"\bholding\b",
    r",\s*.*$",  # everything after comma (sub-entities)
]

def normalize(s):
    """Normalize string for robust fuzzy matching."""
    if not s:
        return ""
    s = s.lower().strip()
    for pat in STRIP_PATTERNS:
        s = re.sub(pat, "", s)
    s = re.sub(r"[^a-zæøåöäü0-9]", "", s)
    return s.strip()

def clean_url(url):
    """Normalize URLs by stripping query parameters."""
    if not url:
        return ""
    return url.split("?")[0].strip()

def get_words(text):
    """Tokenize text into lowercase words."""
    if not text:
        return set()
    text = text.lower()
    text = re.sub(r"[^a-z0-9æøåöäü\s]", " ", text)
    return set(text.split())

def jaccard_similarity(str1, str2):
    """Compute Jaccard similarity coefficient between two strings."""
    words1 = get_words(str1)
    words2 = get_words(str2)
    if not words1 or not words2:
        return 0.0
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    return intersection / union

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

def parse_search_queries():
    default_titles = ["Solution Architect", "Technical Lead", "Senior Software Engineer", "DevOps Engineer"]
    
    if not CONFIG:
        return default_titles

    try:
        titles = set()
        keywords = set()
        
        categories = CONFIG.get("categories", [])
        for cat in categories:
            cat_titles = cat.get("titles", [])
            for t in cat_titles:
                t_strip = t.strip()
                if t_strip:
                    titles.add(t_strip)
            
            cat_keywords = cat.get("keywords", [])
            for k in cat_keywords:
                k_strip = k.strip()
                if k_strip:
                    keywords.add(k_strip)
                    
        search_terms = list(titles)
        if "Terraform" in keywords:
            search_terms.append("Terraform")
        if "DevSecOps" in keywords:
            search_terms.append("DevSecOps")
            
        # Filter out anything too generic
        search_terms = [s for s in search_terms if s.lower() not in ["lead", "architect"]]
            
        return sorted(list(set(search_terms)))
    except Exception as e:
        print(f"Error parsing search queries from config: {e}")
        return default_titles

def run_jobindex_search(query):
    print(f"Running Jobindex search for query: '{query}'...")
    try:
        cmd = ["bun", "run", "src/cli.ts", "search", "--query", query, "--jobage", "14", "--format", "json"]
        result = subprocess.run(cmd, cwd=JOBINDEX_CLI_DIR, capture_output=True, text=True, check=True, encoding="utf-8")
        data = json.loads(result.stdout)
        return data.get("results", [])
    except Exception as e:
        print(f"Error running Jobindex search for '{query}': {e}")
        return []

def run_jobbank_search(query):
    print(f"Running Jobbank search for query: '{query}'...")
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
    # Jobindex format: YYYY-MM-DD
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass
    
    # Jobbank format: Thu, 18 Jun 2026 00:00:00 +0200 or similar
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
    if "remote" in loc_lower or "hjemmearbejde" in loc_lower or "hybrid" in loc_lower:
        return True
        
    location_tiers = CONFIG.get("location_tiers", {})
    ideal_locs = location_tiers.get("ideal", ["copenhagen", "københavn", "storkøbenhavn", "greater copenhagen", "frederiksberg", "hellerup", "glostrup", "ballerup", "kastrup", "herlev", "lyngby", "søborg", "brøndby", "hvidovre", "rødovre", "taastrup", "høje taastrup", "tåstrup"])
    acceptable_locs = location_tiers.get("acceptable", ["roskilde", "hillerød", "køge", "remote", "hybrid", "hjemmearbejde"])
    forbidden_locs = location_tiers.get("too_far", ["jylland", "fyn", "aarhus", "odense", "aalborg", "kolding", "esbjerg", "randers", "horsens", "vejle", "herning", "silkeborg", "svendborg", "sønderborg", "hjørring", "fredericia", "holstebro", "viborg", "skive", "struer"])
    
    ideal_locs = [i.lower() for i in ideal_locs]
    acceptable_locs = [a.lower() for a in acceptable_locs]
    forbidden_locs = [f.lower() for f in forbidden_locs]
    
    has_forbidden = any(f in loc_lower for f in forbidden_locs)
    has_ideal = any(i in loc_lower for i in ideal_locs)
    has_acceptable = any(a in loc_lower for a in acceptable_locs)
    
    if has_forbidden and not has_ideal and not has_acceptable:
        return False
        
    return True

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
    
    fin_companies = ["mastercard", "nets", "danske bank", "nordea", "nykredit", "jyske bank", "simcorp", "saxo bank", "alm. brand", "codan", "tryg"]
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
    print("[START] Starting job scraping workflow...")
    
    # 1. Load State
    seen_jobs = load_seen_jobs()
    applied_jobs = load_applied_jobs()
    search_queries = parse_search_queries()
    
    print(f"Loaded {len(seen_jobs['seen'])} seen jobs.")
    print(f"Loaded {len(applied_jobs)} applied/tracked roles.")
    print(f"Parsed search queries: {search_queries}")
    
    raw_results = []
    
    # 2. Run Parallel Searches
    print(f"Running searches in parallel across portals...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        jobindex_futures = {executor.submit(run_jobindex_search, q): q for q in search_queries}
        jobbank_futures = {executor.submit(run_jobbank_search, q): q for q in search_queries}
        
        # Gather Jobindex results
        for future in concurrent.futures.as_completed(jobindex_futures):
            q = jobindex_futures[future]
            try:
                res = future.result()
                for r in res:
                    r['source_site'] = 'jobindex.dk'
                    raw_results.append(r)
            except Exception as e:
                print(f"Error gathering Jobindex search results for '{q}': {e}")
                
        # Gather Jobbank results
        for future in concurrent.futures.as_completed(jobbank_futures):
            q = jobbank_futures[future]
            try:
                res = future.result()
                for r in res:
                    r['source_site'] = 'jobbank.dk'
                    raw_results.append(r)
            except Exception as e:
                print(f"Error gathering Jobbank search results for '{q}': {e}")
            
    print(f"\nFetched {len(raw_results)} raw postings before filtering.")
    
    # 3. Process & Deduplicate
    unique_jobs = {}
    cutoff_date = datetime.now() - timedelta(days=14)
    
    for job in raw_results:
        title = job.get('title')
        company = job.get('company')
        url = clean_url(job.get('url'))
        
        if not title or not url:
            continue
            
        key = make_key(company, title)
        
        # Check for URL or similarity-based duplicates in unique_jobs
        is_dup = False
        dup_key = None
        for u_key, u_job in unique_jobs.items():
            # Check URL match
            if clean_url(u_job.get('url')) == url:
                is_dup = True
                dup_key = u_key
                break
            # Check title-similarity match for the same company
            if normalize(u_job.get('company', '')) == normalize(company) and jaccard_similarity(u_job.get('title', ''), title) >= 0.75:
                is_dup = True
                dup_key = u_key
                break
                
        if is_dup:
            if len(unique_jobs[dup_key].get('description') or '') < len(job.get('description') or ''):
                # Replace with the richer version of the job details
                unique_jobs[dup_key] = job
            continue
            
        unique_jobs[key] = job
        
    print(f"Deduplicated to {len(unique_jobs)} unique listings.")
    
    # Filter and categorize
    new_matches = []
    skipped_count = 0
    
    for key, job in unique_jobs.items():
        title = job.get('title')
        company = job.get('company', 'Unknown Company') or 'Unknown Company'
        url = clean_url(job.get('url'))
        location = job.get('location', '')
        date_str = job.get('date') or job.get('posted')
        description = job.get('description', '')
        
        # Check against tracker
        tracker_key = f"{company.strip().lower()}|{title.strip().lower()}"
        if tracker_key in applied_jobs:
            skipped_count += 1
            if key in seen_jobs['seen']:
                seen_jobs['seen'][key]['status'] = 'applied'
            continue
            
        # Check if already seen (via exact key, URL, or similarity)
        is_already_seen = False
        seen_key = None
        for s_key, s_job in seen_jobs['seen'].items():
            if s_key == key or clean_url(s_job.get('url')) == url:
                is_already_seen = True
                seen_key = s_key
                break
            if normalize(s_job.get('company', '')) == normalize(company) and jaccard_similarity(s_job.get('title', ''), title) >= 0.75:
                is_already_seen = True
                seen_key = s_key
                break
        
        # Parse date and filter by last 14 days
        job_date = parse_date(date_str)
        if job_date and job_date < cutoff_date:
            continue
            
        # Location filter
        if not is_location_ok(location):
            continue
            
        # Assess fit
        fit = assess_fit(title, company, description)
        
        # Structure seen_jobs metadata
        seen_metadata = {
            "title": title,
            "company": company,
            "url": url,
            "first_seen": seen_jobs['seen'][seen_key].get('first_seen', datetime.now().strftime("%Y-%m-%d")) if is_already_seen else datetime.now().strftime("%Y-%m-%d"),
            "fit": fit,
            "status": "applied" if tracker_key in applied_jobs else ("new" if not is_already_seen else seen_jobs['seen'][seen_key].get('status', 'new'))
        }
        
        # Add to seen_jobs
        if not is_already_seen:
            seen_jobs['seen'][key] = seen_metadata
            new_matches.append({
                "key": key,
                "title": title,
                "company": company,
                "location": location or "Copenhagen Area",
                "url": url,
                "fit": fit,
                "date": job_date.strftime("%Y-%m-%d") if job_date else "Recent",
                "description": description
            })
        else:
            # Just update the record in state without reporting it as a *new* match to user
            seen_jobs['seen'][seen_key] = seen_metadata
            
    # Save the updated seen jobs list
    save_seen_jobs(seen_data=seen_jobs)
    
    # Sort new matches: High -> Medium -> Low
    fit_priority = {"high": 0, "medium": 1, "low": 2}
    new_matches.sort(key=lambda x: fit_priority.get(x['fit'], 2))
    
    high_matches = [m for m in new_matches if m['fit'] == 'high']
    medium_matches = [m for m in new_matches if m['fit'] == 'medium']
    low_matches = [m for m in new_matches if m['fit'] == 'low']
    
    print(f"\nProcessing complete:")
    print(f"  - New matches found: {len(new_matches)}")
    print(f"    - High match: {len(high_matches)}")
    print(f"    - Medium match: {len(medium_matches)}")
    print(f"    - Low match: {len(low_matches)}")
    print(f"  - Already tracked/applied jobs skipped: {skipped_count}")
    
    # 4. Generate Report
    report_content = []
    report_content.append(f"# Job Scraper Report - {datetime.now().strftime('%Y-%m-%d')}\n")
    report_content.append(f"Found {len(new_matches)} new positions matching candidate profile ({len(high_matches)} high, {len(medium_matches)} medium, {len(low_matches)} low match).\n")
    
    if new_matches:
        report_content.append("| # | Fit | Title | Company | Location | Date | Link |")
        report_content.append("|---|-----|-------|---------|----------|------|------|")
        for idx, m in enumerate(new_matches, 1):
            fit_badge = f"**{m['fit'].upper()}**" if m['fit'] == 'high' else m['fit'].capitalize()
            report_content.append(f"| {idx} | {fit_badge} | {m['title']} | {m['company']} | {m['location']} | {m['date']} | [Link]({m['url']}) |")
        
        report_content.append("\n## High-Match Highlights\n")
        if high_matches:
            for idx, m in enumerate(high_matches, 1):
                report_content.append(f"### {idx}. {m['title']} at {m['company']}")
                report_content.append(f"- **URL:** {m['url']}")
                report_content.append(f"- **Location:** {m['location']}")
                
                # Check for specific profile alignments
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
                    
                # Requirements/Risks if any
                report_content.append("- **Requirements to check:** Verify required years of experience in local/regional leadership if mentioned.")
                report_content.append("")
        else:
            report_content.append("No new high-match positions found in this run.\n")
    else:
        report_content.append("No new matching job postings found in this run.\n")
        
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))
        
    print(f"Report written to {REPORT_PATH}")
    
    # Print the report to stdout for the LLM context to capture
    print("\n--- REPORT START ---")
    try:
        print("\n".join(report_content))
    except UnicodeEncodeError:
        print("\n".join(report_content).encode('ascii', errors='replace').decode('ascii'))
    print("--- REPORT END ---")

if __name__ == "__main__":
    main()
