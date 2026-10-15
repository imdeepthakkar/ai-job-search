---
name: add-template
version: 1.0.0
description: >
  Registers a custom LaTeX CV or cover letter template with the AI Job Search framework.
  Accepts a .tex file (plus optional .cls/.sty/font files), captures compilation instructions,
  runs a mandatory test compile, and activates the template by inserting a managed block into
  the appropriate guidance file. Also supports --list and --use <name>. Trigger phrases:
  /add-template, add template, register template, custom cv template, use my own template,
  add cover letter template, add-template --list, add-template --use <name>.
---

<!-- Antigravity wrapper for .claude/commands/add-template.md -->
<!-- Read .claude/commands/add-template.md for the full workflow -->

> **Note on tool names (Antigravity):** Use `view_file` to read files, `write_to_file` to create template files and TEMPLATE.md manifest, `replace_file_content`/`multi_replace_file_content` to edit guidance files, `run_command` for LaTeX compile commands (lualatex/xelatex -interaction=nonstopmode), `list_dir` instead of Glob, and `ask_question` for the interview steps.

Read `.claude/commands/add-template.md` for the complete step-by-step instructions and follow it exactly. The guidance files are `.agents/skills/job-application-assistant/05-cv-templates.md` and `06-cover-letter-templates.md`.
