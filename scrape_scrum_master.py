#!/usr/bin/env python3
import os
import sys
import json
import csv
import re
import subprocess
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN_JOBS_PATH = os.path.join(WORKSPACE_DIR, "job_scraper", "seen_jobs.json")
TRACKER_PATH = os.path.join(WORKSPACE_DIR, "job_search_tracker.csv")
ALL_JOBS_PATH = os.path.join(WORKSPACE_DIR, "job_scraper", "all_scraped_jobs.json")
REPORT_PATH = os.path.join(WORKSPACE_DIR, "scrum_master_jobs_copenhagen.md")

JOBINDEX_CLI = os.path.join(WORKSPACE_DIR, ".agents", "skills", "jobindex-search", "cli")
LINKEDIN_CLI = os.path.join(WORKSPACE_DIR, ".agents", "skills", "linkedin-search", "cli")
JOBBANK_CLI = os.path.join(WORKSPACE_DIR, ".agents", "skills", "jobbank-search", "cli")
JOBNET_CLI = os.path.join(WORKSPACE_DIR, ".agents", "skills", "jobnet-search", "cli")

# Copenhagen Area filters
COPENHAGEN_AREAS = [
    "copenhagen", "københavn", "storkøbenhavn", "greater copenhagen",
    "frederiksberg", "hellerup", "glostrup", "ballerup", "kastrup",
    "herlev", "lyngby", "søborg", "brøndby", "hvidovre", "rødovre",
    "taastrup", "tåstrup", "hillerød", "birkerød", "allerød", "gentofte",
    "virum", "albertslund", "ishøj", "vallensbæk", "dragør", "tårnby",
    "vedbæk", "hørsholm", "kokkedal", "farum", "værløse", "bagsværd",
    "capital region", "hovedstaden", "danmark", "denmark"
]

EXCLUDE_LOCATIONS = [
    "aarhus", "odense", "aalborg", "esbjerg", "randers", "kolding",
    "horsens", "vejle", "roskilde", "herning", "silkeborg", "jylland", "fyn"
]

TARGET_TITLE_PATTERNS = [
    r"\bscrum master\b", r"\bagile coach\b", r"\bagile delivery\b",
    r"\bagile lead\b", r"\bagile leder\b", r"\brelease train engineer\b",
    r"\brte\b", r"\bagile project manager\b"
]

# Negative patterns in title
NEGATIVE_TITLE_PATTERNS = [
    r"\bmaster data\b", r"\bdata master\b", r"\bmaster planner\b",
    r"\bgame master\b", r"\bgamemaster\b", r"\bpostdoc\b", r"\bph\.?d\b",
    r"\btrainee\b", r"\bstudent\b", r"\bintern\b", r"\bpraktik\b",
    r"\bmaskinsnedker\b", r"\bunderviser\b", r"\btimelærer\b", r"\blektor\b", r"\badjunkt\b"
]

STRIP_PATTERNS = [
    r"\ba/s\b", r"\baps\b", r"\bi/s\b", r"\bp/s\b", r"\bk/s\b",
    r"\bivs\b", r"\bamba\b", r"\ba\.m\.b\.a\.\b",
    r"\(.*?\)",
    r"\bdanmark\b", r"\bdenmark\b", r"\bscandinavia\b", r"\bnordic\b",
    r"\bgroup\b", r"\bholding\b", r"\bstore nord\b",
    r",\s*.*$",
]

def normalize(text):
    if not text:
        return ""
    text = text.lower().strip()
    for pat in STRIP_PATTERNS:
        text = re.sub(pat, "", text)
    text = re.sub(r"[^a-z0-9æøå]", "", text)
    return text.strip()

def slugify(text):
    text = (text or "").lower()
    text = text.replace('æ', 'ae').replace('ø', 'oe').replace('å', 'aa')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def make_key(company, title):
    c_slug = slugify(company or "unknown")[:30]
    t_slug = slugify(title or "unknown")[:30]
    return f"{c_slug}-{t_slug}"

def is_valid_scrum_master_title(title):
    if not title:
        return False
    t_lower = title.lower()
    for neg in NEGATIVE_TITLE_PATTERNS:
        if re.search(neg, t_lower):
            return False
    for pos in TARGET_TITLE_PATTERNS:
        if re.search(pos, t_lower):
            return True
    return False

def is_in_copenhagen(location):
    if not location:
        return True
    loc_lower = location.lower()
    if any(ex in loc_lower for ex in EXCLUDE_LOCATIONS) and not any(cop in loc_lower for cop in ["københavn", "copenhagen", "storkøbenhavn"]):
        return False
    if "remote" in loc_lower or "hjemmearbejde" in loc_lower:
        return True
    return any(c in loc_lower for c in COPENHAGEN_AREAS)

def run_cmd(cmd, cwd):
    try:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True, encoding="utf-8")
        return json.loads(res.stdout)
    except Exception as e:
        return None

def fetch_linkedin_details(job_id):
    try:
        res = subprocess.run(["bun", "run", "src/cli.ts", "detail", str(job_id), "--format", "json"],
                             cwd=LINKEDIN_CLI, capture_output=True, text=True, check=True, encoding="utf-8")
        data = json.loads(res.stdout)
        return data.get("description")
    except Exception:
        return None

def fetch_jobindex_details(job_id):
    try:
        res = subprocess.run(["bun", "run", "src/cli.ts", "detail", str(job_id), "--format", "json"],
                             cwd=JOBINDEX_CLI, capture_output=True, text=True, check=True, encoding="utf-8")
        data = json.loads(res.stdout)
        return data.get("description")
    except Exception:
        return None

def load_applied_jobs():
    applied = set()
    if os.path.exists(TRACKER_PATH):
        try:
            with open(TRACKER_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    c = normalize(row.get("company", ""))
                    r = normalize(row.get("role", ""))
                    if c and r:
                        applied.add(f"{c}|{r}")
        except Exception as e:
            print(f"Warning loading tracker: {e}")
    return applied

def load_seen_jobs():
    if os.path.exists(SEEN_JOBS_PATH):
        try:
            with open(SEEN_JOBS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "seen" in data:
                    return data
        except Exception as e:
            print(f"Warning loading seen_jobs: {e}")
    return {"seen": {}}

def main():
    print("=== Scraping Scrum Master & Agile Delivery Jobs in Greater Copenhagen ===")
    all_raw = []

    # 1. Jobindex
    print("\n--- Querying Jobindex ---")
    ji_queries = ['"Scrum Master"', '"Agile Coach"', 'scrum master københavn', '"Agile Delivery"']
    for q in ji_queries:
        print(f"Jobindex query: {q}")
        data = run_cmd(["bun", "run", "src/cli.ts", "search", "--query", q, "--jobage", "30", "--format", "json"], JOBINDEX_CLI)
        if data and "results" in data:
            for item in data["results"]:
                item["source"] = "jobindex.dk"
                all_raw.append(item)

    # 2. LinkedIn
    print("\n--- Querying LinkedIn ---")
    li_queries = ["Scrum Master", "Agile Coach", "Release Train Engineer"]
    for q in li_queries:
        for page in [1, 2, 3]:
            print(f"LinkedIn query: {q} (page {page})")
            data = run_cmd(["bun", "run", "src/cli.ts", "search", "--query", q, "--location", "Copenhagen, Capital Region, Denmark", "--jobage", "30", "--page", str(page), "--format", "json"], LINKEDIN_CLI)
            if data and "results" in data:
                for item in data["results"]:
                    item["source"] = "linkedin.com"
                    all_raw.append(item)

    # 3. Jobnet
    print("\n--- Querying Jobnet ---")
    jn_queries = ["Scrum Master", "Agile Coach"]
    for q in jn_queries:
        print(f"Jobnet query: {q}")
        data = run_cmd(["bun", "run", "src/cli.ts", "search", "--search-string", q, "--region", "HovedstadenOgBornholm", "--format", "json"], JOBNET_CLI)
        if data and "results" in data:
            for item in data["results"]:
                pub_date = item.get("publicationDate", "")
                if pub_date:
                    pub_date = pub_date[:10]
                dl = item.get("applicationDeadline", "")
                if dl:
                    dl = dl[:10]
                loc = item.get("postalDistrictName") or item.get("municipality") or "Storkøbenhavn"
                job_url = f"https://jobnet.dk/Findjob/Jobannonce?JobannonceId={item.get('jobAdId')}"
                all_raw.append({
                    "id": item.get("jobAdId"),
                    "title": item.get("title"),
                    "company": item.get("hiringOrgName"),
                    "location": loc,
                    "date": pub_date,
                    "deadline": dl,
                    "url": job_url,
                    "description": None,
                    "source": "jobnet.dk"
                })

    # 4. Jobbank
    print("\n--- Querying Jobbank ---")
    jb_queries = ["scrum master", "agile coach"]
    for q in jb_queries:
        print(f"Jobbank query: {q}")
        data = run_cmd(["bun", "run", "src/cli.ts", "search", "--key", q, "--location", "2", "--format", "json"], JOBBANK_CLI)
        if data and "results" in data:
            for item in data["results"]:
                item["source"] = "jobbank.dk"
                all_raw.append(item)

    print(f"\nTotal raw listings fetched: {len(all_raw)}")

    # Deduplicate and Filter
    applied = load_applied_jobs()
    seen_data = load_seen_jobs()
    seen_map = seen_data.get("seen", {})

    unique_jobs = {}
    for r in all_raw:
        title = (r.get("title") or "").strip()
        company = (r.get("company") or "").strip()
        location = (r.get("location") or "").strip()
        url = (r.get("url") or "").strip()

        if not is_valid_scrum_master_title(title):
            continue
        if not is_in_copenhagen(location):
            continue

        norm_comp = normalize(company)
        norm_tit = normalize(title)
        key = f"{norm_comp}|{norm_tit}"
        slug_key = make_key(company, title)

        is_applied = key in applied

        # Check if already in unique_jobs by fuzzy match
        matched_key = None
        for k, existing in unique_jobs.items():
            existing_comp = normalize(existing["company"])
            existing_tit = normalize(existing["title"])
            comp_match = (norm_comp == existing_comp) or (norm_comp in existing_comp and len(norm_comp) >= 3) or (existing_comp in norm_comp and len(existing_comp) >= 3)
            tit_match = (norm_tit == existing_tit) or (norm_tit in existing_tit and len(norm_tit) >= 10) or (existing_tit in norm_tit and len(existing_tit) >= 10)
            if comp_match and tit_match:
                matched_key = k
                break

        if not matched_key:
            unique_jobs[key] = {
                "key": slug_key,
                "title": title,
                "company": company,
                "location": location or "Greater Copenhagen",
                "date": r.get("date"),
                "deadline": r.get("deadline"),
                "url": url,
                "source": r.get("source"),
                "id": r.get("id"),
                "applied": is_applied,
                "seen": slug_key in seen_map or url in [v.get("url") for v in seen_map.values()],
                "description": r.get("description")
            }
        else:
            existing = unique_jobs[matched_key]
            if not existing.get("deadline") and r.get("deadline"):
                existing["deadline"] = r.get("deadline")
            if not existing.get("date") and r.get("date"):
                existing["date"] = r.get("date")
            if "source" in existing and r.get("source") not in existing["source"]:
                existing["source"] = f"{existing['source']}, {r.get('source')}"

    scrum_jobs = list(unique_jobs.values())
    print(f"Found {len(scrum_jobs)} confirmed Scrum Master / Agile Lead positions in Greater Copenhagen.")

    # Fetch detailed descriptions for top matches if missing
    for j in scrum_jobs:
        if not j.get("description"):
            if j["source"] == "linkedin.com" and j.get("id"):
                print(f"Fetching LinkedIn details for {j['title']} at {j['company']}...")
                j["description"] = fetch_linkedin_details(j["id"])
            elif j["source"] == "jobindex.dk" and j.get("id"):
                print(f"Fetching Jobindex details for {j['title']} at {j['company']}...")
                j["description"] = fetch_jobindex_details(j["id"])

    # Sort by date descending
    scrum_jobs.sort(key=lambda x: str(x.get("date") or "2000-01-01"), reverse=True)

    # Generate Markdown Report
    report = []
    report.append("# Scrum Master & Agile Delivery Jobs in Greater Copenhagen")
    report.append(f"\n*Scraped on {datetime.now().strftime('%Y-%m-%d %H:%M')} across Jobindex, LinkedIn, Jobnet, and Jobbank.*\n")
    report.append(f"**Total relevant positions found:** {len(scrum_jobs)}\n")

    report.append("| # | Job Title | Company | Location | Posted | Deadline | Source | Status | Link |")
    report.append("|---|-----------|---------|----------|--------|----------|--------|--------|------|")

    for i, j in enumerate(scrum_jobs, 1):
        status_badge = "✅ Applied" if j["applied"] else ("👀 Seen" if j["seen"] else "✨ **NEW**")
        dl = j.get("deadline") or "Løbende / ASAP"
        dt = j.get("date") or "Recent"
        report.append(f"| {i} | **{j['title']}** | {j['company']} | {j['location']} | {dt} | {dl} | {j['source']} | {status_badge} | [View Job]({j['url']}) |")

    report.append("\n---\n")
    report.append("## Detailed Breakdown of Positions\n")

    for i, j in enumerate(scrum_jobs, 1):
        report.append(f"### {i}. {j['title']} – {j['company']}")
        report.append(f"- **Company:** {j['company']}")
        report.append(f"- **Location:** {j['location']}")
        report.append(f"- **Posted Date:** {j.get('date') or 'N/A'}")
        report.append(f"- **Application Deadline:** {j.get('deadline') or 'Løbende / ASAP'}")
        report.append(f"- **Platform / Source:** {j['source']}")
        report.append(f"- **URL:** [{j['url']}]({j['url']})")
        if j.get("description"):
            desc_clean = re.sub(r'\s+', ' ', j["description"]).strip()
            desc_snip = " ".join(desc_clean.split()[:90]) + "..."
            report.append(f"- **Summary / Highlights:** {desc_snip}")
        report.append("")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"\nReport written to: {REPORT_PATH}")

    # Output JSON summary
    json_summary_path = os.path.join(WORKSPACE_DIR, "job_scraper", "scrum_master_results.json")
    with open(json_summary_path, "w", encoding="utf-8") as f:
        json.dump(scrum_jobs, f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {json_summary_path}")

if __name__ == "__main__":
    main()
