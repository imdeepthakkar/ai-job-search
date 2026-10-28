# Smart Auto-Proceed in Apply Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure `/apply` to automatically draft, review, compile PDFs, and back up to Google Drive without stopping for user permission when a job matches, pausing only on poor fit or dealbreaker vetoes.

**Architecture:** Update workspace rules in `.agents/AGENTS.md` and the Step 1 evaluation decision gate in `.agents/skills/apply/SKILL.md` and `.claude/commands/apply.md` with explicit conditional logic.

**Tech Stack:** Markdown specifications, Antigravity Agent Rules, Pytest.

## Global Constraints
- Do not bypass user confirmation if the job fit score is < 60 or trips a hard dealbreaker veto (location, authorization, language).
- Maintain all existing verification, LaTeX compilation non-interactive flags, and Google Drive upload steps.
- Preserve candidate profile files and existing testing integrity.

---

### Task 1: Add Workspace Rule to `.agents/AGENTS.md`

**Files:**
- Modify: `.agents/AGENTS.md`

**Interfaces:**
- Consumed by: Antigravity root agent & subagents reading workspace directives.

- [ ] **Step 1: Edit `.agents/AGENTS.md` to append the Autonomous Application Workflow rule**
- [ ] **Step 2: Verify git diff for `.agents/AGENTS.md`**

---

### Task 2: Update Step 1 Decision Gate in Apply Workflow Specs

**Files:**
- Modify: `.agents/skills/apply/SKILL.md`
- Modify: `.claude/commands/apply.md`

**Interfaces:**
- Consumed by: `/apply` skill execution during job evaluation and transition to drafting.

- [ ] **Step 1: Update `.claude/commands/apply.md` lines 77–80 with conditional auto-proceed logic**
- [ ] **Step 2: Update `.agents/skills/apply/SKILL.md` with the matching conditional auto-proceed instructions**
- [ ] **Step 3: Verify git diff for both files**

---

### Task 3: Verification and Test Suite Execution

**Files:**
- Test: `tests/test_apply_records_application.py`
- Test: `tests/test_security_guards.py`

- [ ] **Step 1: Run pytest on apply-related test suites**
- [ ] **Step 2: Run security guard checks**
- [ ] **Step 3: Commit and push changes**
