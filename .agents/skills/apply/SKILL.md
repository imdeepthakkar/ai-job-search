---
name: apply
version: 1.0.0
description: >
  Drafter-Reviewer job application workflow: evaluates a job posting for fit,
  drafts a tailored CV and cover letter, spawns a reviewer subagent for critique,
  revises based on feedback, compiles PDFs, runs ATS keyword verification, and
  presents the final output. Use when the user provides a job posting URL or text
  and wants to apply. Trigger phrases: /apply, apply to job, draft application,
  write cv for, write cover letter for, apply for this job, job posting URL.
---

<!-- This skill wraps the /apply command from .claude/commands/apply.md -->
<!-- Read that file for the full workflow instructions -->

You are orchestrating a two-agent job application workflow. The job posting is provided (either a URL or pasted text).

Follow these steps **exactly in order**. Do not skip steps.

**Token-efficiency rules for this workflow:**
- Never re-read a file whose contents are already in your context from an earlier step.
- When dispatching the reviewer agent, pass draft content **inline in the agent prompt** rather than asking the agent to read files you already have in memory.
- Run the full verification checklist exactly once, at the end (Step 6). The reviewer focuses on content critique, not verification.
- Step 5 (compile and inspect PDFs) is mandatory and non-skippable.

> **Note on tool names (Antigravity):** Use `view_file` to read files, `write_to_file`/`replace_file_content`/`multi_replace_file_content` to write/edit, `run_command` to run shell commands, `search_web`/`read_url_content` for web research, and `browser_subagent` to dispatch a reviewer subagent. The full workflow is defined in `.claude/commands/apply.md` — read it now before proceeding.

<!-- Load the full workflow -->
See `.claude/commands/apply.md` for the complete step-by-step instructions. Read that file and follow it exactly, substituting Antigravity tool names where needed:
- `WebFetch` → `read_url_content` or `browser_subagent`
- `WebSearch` → `search_web`
- `Read` → `view_file`
- `Write` → `write_to_file`
- `Edit` → `replace_file_content` or `multi_replace_file_content`
- `Bash(...)` → `run_command`
- `Agent` (reviewer subagent) → `browser_subagent` with a research-focused task
- `AskUserQuestion` → `ask_question`

The skill reference files live in `.agents/skills/job-application-assistant/` (Antigravity) — use those paths instead of `.claude/skills/job-application-assistant/`.

**Autonomous Progression (Auto-Proceed on Match):**
- When the job evaluation (Step 1) indicates a **match** (score >= 60, no hard vetoes), **do NOT pause or wait for user confirmation**. Proceed directly through drafting, review, LaTeX compilation, and Google Drive upload.
- **Only stop and prompt the user** if the posting is a **mismatch** (score < 60) or triggers a hard dealbreaker veto (location, authorization, language).

**Google Drive Backup:**
At the end of Step 6, run:
```bash
python tools/upload_to_gdrive.py --latest --optional
```
to automatically upload the newly compiled CV and cover letter PDFs to Google Drive if credentials are configured.
