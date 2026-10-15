---
name: gmail-sync
version: 1.0.0
description: >
  Syncs application status from Gmail: scans Gmail for status signals (interview
  invites, assessment links, offers, rejections) on tracked applications, classifies
  them, presents a batch of proposed updates for approval, then writes to
  job_search_tracker.csv and outcome.md only after the user approves. Requires
  Gmail MCP integration (Notion MCP or Gmail connector). Trigger phrases: /gmail-sync,
  sync gmail, check email for job updates, scan gmail, email sync, gmail applications.
---

<!-- Antigravity wrapper for .claude/commands/gmail-sync.md -->
<!-- Read .claude/commands/gmail-sync.md for the full workflow -->

> **Note on tool names (Antigravity):** This command uses Gmail MCP tools. Check if `mcp__claude_ai_Gmail__*` tools are available. Use `view_file` to read files, `replace_file_content`/`multi_replace_file_content` to edit, and `ask_question` to present the batch of proposed updates for user approval before writing.

Read `.claude/commands/gmail-sync.md` for the complete step-by-step instructions and follow it exactly.
