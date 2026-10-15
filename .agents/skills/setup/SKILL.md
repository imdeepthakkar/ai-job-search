---
name: setup
version: 1.0.0
description: >
  Profile onboarding / setup workflow: collects professional information and
  populates all profile skill files so the apply workflow works out of the box.
  Three paths: Path A reads existing documents/, Path B imports a single CV,
  Path C walks through structured interview questions. Also handles section updates
  with --section <name>. Trigger phrases: /setup, setup profile, onboard, populate profile,
  import cv, setup job search, configure search queries.
---

<!-- Antigravity wrapper for .claude/commands/setup.md -->
<!-- Read .claude/commands/setup.md for the full workflow -->

> **Note on tool names (Antigravity):** Use `view_file` to read files, `write_to_file`/`replace_file_content`/`multi_replace_file_content` to write/edit, `run_command` to run shell commands, `list_dir`/`grep_search` instead of Glob/Grep, `search_web`/`read_url_content` for web research, and `ask_question` to ask the user structured questions.

Read `.claude/commands/setup.md` for the complete step-by-step instructions and follow it exactly. The skill files live in `.agents/skills/job-application-assistant/` on this system (not `.claude/skills/`).
