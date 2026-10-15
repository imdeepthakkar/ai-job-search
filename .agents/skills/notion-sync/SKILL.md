---
name: notion-sync
version: 1.0.0
description: >
  Pushes ranked jobs and tracked applications to a Notion database as a read-only
  pipeline view. One-way sync: repo files stay the system of record. Requires Notion
  MCP server (OAuth). Creates or upserts database rows for jobs scored >= 60 (configurable)
  and all tracked applications. Trigger phrases: /notion-sync, sync to notion, push to notion,
  notion pipeline, notion dashboard, update notion, publish jobs to notion.
---

<!-- Antigravity wrapper for .claude/commands/notion-sync.md -->
<!-- Read .claude/commands/notion-sync.md for the full workflow -->

> **Note on tool names (Antigravity):** This command uses Notion MCP tools (available via the `notion` MCP server in this session). Use `view_file` to read local files, `replace_file_content` to update the sync state file, and call Notion MCP tools via `call_mcp_tool` with ServerName "notion".

Read `.claude/commands/notion-sync.md` for the complete step-by-step instructions and follow it exactly.
