---
name: reset
version: 1.0.0
description: >
  Resets candidate profile data back to a blank state. Scope options: "profile" clears
  01-candidate-profile.md, 02-behavioral-profile.md, profile statements in 05, and STAR
  examples in 07; "documents" deletes files in documents/; "all" does both. Requires
  explicit RESET confirmation before writing anything. Trigger phrases: /reset, reset profile,
  clear profile, start over, reset job search, wipe profile data, reset all.
---

<!-- Antigravity wrapper for .claude/commands/reset.md -->
<!-- Read .claude/commands/reset.md for the full workflow -->

> **Note on tool names (Antigravity):** Use `view_file` to read files, `write_to_file` (Overwrite: true) or `replace_file_content` to replace profile file content with blank templates, `run_command` to delete document files (rm -f), `list_dir` instead of Glob, and `ask_question` to get the scope and the explicit RESET confirmation before doing anything destructive.

Read `.claude/commands/reset.md` for the complete step-by-step instructions and follow it exactly. The skill files live in `.agents/skills/job-application-assistant/` on this system.
