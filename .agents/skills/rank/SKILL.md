---
name: rank
version: 1.0.0
description: >
  Batch-scores scraped jobs into a ranked shortlist. Dispatches parallel subagents
  to fetch and score each posting against the fit framework, applies location vetoes
  and deadline urgency, and presents a ranked table with verdicts. Run after /scrape.
  Trigger phrases: /rank, rank jobs, score jobs, prioritize jobs, rank scraped jobs,
  which jobs to apply to, best jobs for me.
---

<!-- Antigravity wrapper for .claude/commands/rank.md -->
<!-- Read .claude/commands/rank.md for the full workflow -->

> **Note on tool names (Antigravity):** Use `view_file` to read files, `write_to_file`/`replace_file_content` to write/edit, `run_command` for shell commands, `search_web`/`read_url_content` for web research, `ask_question` for questions, and `browser_subagent` to dispatch parallel scoring subagents (equivalent to Claude Code's Agent tool).

Read `.claude/commands/rank.md` for the complete step-by-step instructions and follow it exactly. The skill files live in `.agents/skills/job-application-assistant/` on this system.
