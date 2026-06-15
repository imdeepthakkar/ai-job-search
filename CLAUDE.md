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
- [ ] Formatting: Helvetica/Arial font for Danish professional standards
- [ ] Links: Remove hyperlinks from Email/LinkedIn for hardcopy/ATS safety if requested
- [ ] Compiled PDF verification: Check for orphaned titles and overflow
