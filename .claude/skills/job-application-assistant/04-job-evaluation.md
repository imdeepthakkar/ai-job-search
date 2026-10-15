# Job Evaluation Framework

This framework helps Claude evaluate how well a job posting matches Deep Thakkar's profile and career goals.

## Language Gate — run before scoring

This gate checks a posting's language requirements against what the candidate actually speaks. It is not one of the five Scoring Dimensions below - it runs before them, structured the same way as the Eligibility Gate above: read the posting, classify against profile data, and treat a hard mismatch as FAIL before scoring. Its verdict is tracked downstream: `/rank` records the result as `language_gate` (PASS/FAIL/FLAG) with a supporting `language_note`, persists both into `seen_jobs.json`, and treats a FAIL as a shortlist veto; `/scrape` surfaces the flag in its results table and carries a language-override rule for postings whose ad language differs from the role's working language. `/apply`'s language detection (Step 1, which extracts a posting's required language generically) feeds this same check.

Read the posting's language requirements as stated for **the role itself** — not the language the ad happens to be written in. A posting written in a language you don't work in, for a role that only needs languages you do work in on the job, passes fine; only an explicit job-condition requirement ("fluent X required," "must communicate with the Y team in Z") triggers this check. For each language the posting requires as a job condition, compare it against your Languages table in `01-candidate-profile.md`:

| Posting requirement vs. your Languages table | Verdict |
|---|---|
| Requires a language **not on your table at all** (e.g. "fluent Polish required," "must communicate with the Warsaw team in Russian," and you list no Polish/Russian row) | **FAIL — hard stop.** Do not score, do not draft. Quote the exact requirement line. |
| Requires a language you **do** list, but the posting's stated bar (as written — "fluent," "native," "C1+," "business-level") reads as plausibly **higher** than your declared level | **FLAG, then proceed.** Not a fail. Score and draft normally, but surface the gap explicitly in your report to the user (quote both the posting's requirement and your declared level) so they can judge it themselves — bars like "fluent" vary a lot by company and geography, and a recruiter may be flexible. Never silently drop the posting and never silently treat it as a clean pass. |
| Requires a language you list, at or below your declared level (or the posting doesn't specify a level at all — just names the language) | **PASS.** No note needed. |

Judge the level comparison the same way you judge everything else in this framework: read both sides as written and reason about it, don't force either into a rigid scale — CEFR letters, LinkedIn-style buckets ("professional working proficiency"), and plain-English words ("conversational," "fluent," "native") all appear in the wild and don't map onto each other precisely. When genuinely unsure whether a stated bar exceeds the candidate's level, prefer FLAG over a silent PASS — the human is meant to be the tiebreaker, not the gate.

**Worked example:** a candidate whose Languages table lists Danish (Conversational/B1) and English (Fluent/C1). A posting requiring "fluent Polish" → **FAIL**, Polish isn't declared at all. A posting requiring "flydende dansk" → **FLAG**, Danish is declared but "flydende" plausibly exceeds B1 — score and draft the application, but tell the candidate this posting's bar may be a stretch and let them decide. A posting requiring "English" or conversational Danish → **PASS**.

## Skill Match Areas

### Strong Match (Target)
- Cloud Architecture (Azure/AWS)
- Infrastructure as Code (Terraform)
- Modernization & Microservices
- Security & Compliance (Financial/Regulated)
- Technical Leadership & Mentorship
- Stakeholder Management (C-level)

### Moderate Match
- Kubernetes & Docker
- CI/CD (GitLab, Jenkins, GitHub Actions)
- Java/Platform Engineering
- Technical Writing & Advocacy

### Weak Match (Gap)
- Low-level programming (C/C++)
- Frontend-heavy roles
- Non-cloud legacy system administration (without a modernization focus)

## Career Goals & Motivation Filters

### Primary Goals
- Secure a Senior Solutions Architect or Technical Lead role in the Copenhagen area (or remote/hybrid).
- Focus on high-impact projects involving cloud acceleration, modernization, or secure infrastructure.
- Maintain a 'Trusted Advisor' status with business stakeholders.

### Motivation Filters
- **Positive Signals:** Focus on innovation, cloud-native adoption, large-scale systems, mentorship opportunities, and international teams.
- **Negative Signals:** Lack of technical leadership, "maintenance-only" roles without growth, purely manual infrastructure management.

## Location & Commute
- **Ideal:** Copenhagen area (København, Hellerup, Ballerup).
- **Acceptable:** Sjælland (within 45-60 min commute).
- **Borderline:** Remote/Hybrid roles with occasional travel to Aarhus or Odense.
- **Too Far:** Full-time on-site outside of Sjælland.

## Salary Baseline
*[Not explicitly provided - default to market rates for Senior Architects in Denmark]*
- Expected range: 75,000 - 100,000 DKK/month + pension (market standard for high-seniority architects).
