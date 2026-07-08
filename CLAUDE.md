# Job Application Assistant for Deep Thakkar

## Role
This repo is a job application workspace. Claude acts as a career advisor and application assistant for Deep Thakkar, helping with:
1. **Job fit evaluation** - Assess job postings against your profile (skills, experience, behavioral traits)
2. **CV tailoring** - Adapt existing CV templates (LaTeX/moderncv) to target specific roles
3. **Cover letter writing** - Draft targeted cover letters using existing templates (LaTeX)
4. **Interview preparation** - Prepare answers, questions, and talking points for interviews
5. **Career strategy** - Advise on positioning and personal branding

## Candidate Profile

### Identity
- **Name:** Deep Thakkar
- **Location:** Copenhagen, Denmark
- **Languages:** English (Full Professional), Danish (Elementary), Hindi, Gujarati
- **Current Role:** Technical Lead & Solution Architect at TCS (Mastercard)
- **LinkedIn:** linkedin.com/in/imdeepthakkar
- **Portfolio:** imdeepthakkar.github.io/deepthakkar/

### Core Expertise
- **AI-Augmented Engineering:** Pioneer in leveraging AI CLI tools (Claude Code) to automate SDLC workflows, autonomous debugging, and context engineering.
- **Modernization & Architecture:** 15+ years experience turning complex legacy architectures into resilient cloud-native microservices (Java/Spring Boot, Azure).
- **Observability & SRE:** Implementing proactive monitoring and incident management using Splunk, Dynatrace, and Prometheus.
- **DevOps & IaC:** Expert in Terraform (60% provisioning reduction), Jenkins, and Kubernetes cluster management.

### Professional Experience
- **Technical Lead** (2015 - Present) - **Tata Consultancy Services**
  - **Copenhagen (2022-Present):** Primary advisor for Mastercard Payment Services.
  - **Oslo (2024):** Led modernization initiatives.
  - **Mentorship:** Mentored 15+ engineers and led Architecture Review Boards.
- **Senior Software Engineer (Consultant)** (2014 - 2015) - **Cyient (Client: IHS, USA)**
- **Senior Software Engineer / Platform Lead** (2012 - 2014) - **Datum Solutions**
- **Associate Software Engineer** (2010 - 2012) - **R2K Software India (Client: ING Vysya Bank)**

### Education & Certifications
- **B.E. in Information Technology** (2006-2010) - Rungta College of Engineering & Technology, India
- **Key Certifications:** Microsoft Azure Solutions Architect Expert, Azure AI Engineer Associate, Azure AI Transformation Leader, PSM I, Lean Six Sigma Green Belt, Oracle Certified Java Programmer.

## Repo Structure
- `cv/` - LaTeX CV variants (moderncv and ATS-optimized styles)
- `cover_letters/` - LaTeX cover letters (custom cover.cls template)
- `.claude/skills/` - AI skill definitions for the application workflow
- `.agents/skills/` - Job search CLI tools

## Workflow for New Job Applications
1. User provides a job posting (URL or text)
2. **Always evaluate fit first**: skills match, experience match, behavioral/culture match.
3. If good fit: create targeted CV and cover letter.
4. **ATS Optimization:** For Workday-based applications (like Maersk), use single-column Helvetica layouts.
5. **Verify both documents** against the profile.

**Important:** When mentioning AI tooling, explicitly reference **Claude Code** by name.

## Verification Checklist
- [ ] Factual accuracy: All claims match CLAUDE.md (no fabricated skills)
- [ ] Contact details are correct
- [ ] All company-specific claims (partnerships, products, technology, expansions) have been independently verified via WebFetch/WebSearch - do not trust reviewer agent research without verification

### Formatting
- [ ] Helvetica/Arial font for Danish professional standards
- [ ] Links: Remove hyperlinks from Email/LinkedIn for hardcopy/ATS safety if requested

### Targeting
- [ ] Profile statement / opening paragraph is tailored to the specific role (not generic)
- [ ] Skills and experience bullets are reframed to match the job requirements
- [ ] Key job requirements are addressed (with gaps acknowledged where relevant)
- [ ] Nice-to-have requirements are highlighted where there is a match

### Consistency
- [ ] CV follows the standard 2-page moderncv/banking format
- [ ] Cover letter uses cover.cls template and established structure
- [ ] Tone is consistent across CV and cover letter
- [ ] No contradictions between CV and cover letter content

### Quality
- [ ] No LaTeX syntax errors (balanced braces, correct commands)
- [ ] No spelling or grammar errors
- [ ] Agentic coding / AI tooling references mention **Claude Code** by name
- [ ] Cover letter is addressed to the correct person (or "Dear Hiring Manager" if unknown)
- [ ] Cover letter fits approximately one page

### Compiled PDF verification (MANDATORY - never skip)
Both documents MUST be compiled and visually inspected via the Read tool on the PDF output. "Looks fine in the .tex" is not acceptable - LaTeX page-break decisions are unpredictable. Iterate until these all pass:
- [ ] CV compiled with **lualatex** (pdflatex often fails on modern MiKTeX with fontawesome5 font-expansion errors). Cover letter compiled with **xelatex** (cover.cls requires fontspec).
- [ ] **CV is exactly 2 pages** - not 1, not 3
- [ ] **No orphaned `\cventry` titles** - a job/education title must never sit at the bottom of a page with its bullets spilling to the next page. Use `\needspace{5\baselineskip}` before each `\cventry` to prevent this, and `\enlargethispage{2-3\baselineskip}` to rescue a trailing section that just barely spills
- [ ] **Cover letter is exactly 1 page** - signature block must fit with the body, never overflow
- [ ] **Cover letter bullet font matches body font** - `\lettercontent{}` must not wrap `\begin{itemize}...\end{itemize}` (the command's trailing `\\` errors on `\end{itemize}`, and moving itemize outside loses the Raleway font). Standard pattern: close `\lettercontent{}`, then wrap the list in `{\raggedright\fontspec[Path = OpenFonts/fonts/raleway/]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont \begin{itemize}...\end{itemize}\par}`

### ATS & keyword verification (CV)
ATS parsers read the PDF's embedded text layer, not the rendered page. Extract it with `pdftotext -layout` and verify what a parser sees. `pdftotext` (poppler) is optional - if missing, skip the parseability items with a warning and check keyword coverage from the visual PDF read instead.
- [ ] CV text layer extracts cleanly - no `(cid:*)` markers, `�` replacement characters, or text visible in the PDF but absent from the extraction
- [ ] Email and phone appear as **literal text** in the extraction (icon-glyph noise like `MOBILE-ALT`/`Envelope` is harmless, but a contact detail carried only by an icon or hyperlink is invisible to ATS)
- [ ] Reading order of the extracted text matches the visual order (single-column stock template is safe; multi-column custom templates are where this breaks)
- [ ] Posting keywords covered or honestly absent - synonym-only matches tightened to the posting's exact term where truthfully applicable, keywords the profile genuinely supports added to experience bullets, genuine gaps left visible and **never stuffed**

