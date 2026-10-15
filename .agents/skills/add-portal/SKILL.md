---
name: add-portal
version: 1.0.0
description: >
  Generates a job-portal search skill for any local job board market. Investigates
  the portal's API/HTML structure, scaffolds a TypeScript CLI skill following the
  portal-skill contract (same as linkedin-search), runs a live test query, and
  registers the skill in .agents/skills/. Country-agnostic generator. Trigger phrases:
  /add-portal, add job portal, add new job board, create portal skill, add <portal name> skill,
  add-portal --list.
---

<!-- Antigravity wrapper for .claude/commands/add-portal.md -->
<!-- Read .claude/commands/add-portal.md for the full workflow -->

> **Note on tool names (Antigravity):** Use `view_file` to read files, `write_to_file` to create new skill files, `run_command` for bash commands (bun install, typecheck, live test), `read_url_content`/`search_web` for portal investigation, `list_dir` instead of Glob, and `ask_question` for the interview steps.

Read `.claude/commands/add-portal.md` for the complete step-by-step instructions and follow it exactly. The canonical reference example is `.agents/skills/linkedin-search/`.
