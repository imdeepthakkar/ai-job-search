# Design Spec: Smart Auto-Proceed for Job Applications

- **Date:** 2026-10-28
- **Author:** Deep Thakkar & Antigravity
- **Status:** Approved

---

## 1. Context and Problem Statement

When running `/apply` with a job posting URL or text, the workflow traditionally evaluates the posting against the candidate profile in Step 1 and then halts with an interactive prompt:
```text
"Should I proceed with drafting the CV and cover letter for this role?"
```
This forces the user to manually reply "Yes" every time before the agent begins drafting, reviewing, compiling LaTeX PDFs, and uploading to Google Drive.

The user's primary goal is to obtain the final tailored CV and cover letter PDFs directly. Manual intervention should only occur if the job does not match the candidate's profile or triggers an explicit dealbreaker veto.

---

## 2. Goals & Non-Goals

### Goals
- Make `/apply` an automated, continuous pipeline from URL/text input to compiled PDFs and Google Drive backup when a job matches.
- Gate drafting only when a role is a poor fit (overall score < 60) or triggers a hard dealbreaker veto (location/relocation, visa/authorization, or mandatory language requirements).
- Preserve all existing evaluation rigor, factual grounding audits, ATS verification, LaTeX quality checks, and Google Drive upload rules.

### Non-Goals
- Changing the fit evaluation scoring rubrics or veto categories defined in `04-job-evaluation.md`.
- Bypassing user confirmation when a hard veto or poor fit is detected.
- Altering the PDF compilation or file naming standards.

---

## 3. Detailed Design

### 3.1 Workspace Rules (`.agents/AGENTS.md`)
Add an explicit workspace-level instruction under `Workspace Rules`:

```markdown
- **Autonomous Application Workflow (Auto-Proceed on Match)**:
  During the `/apply` workflow:
  - If the job evaluation results in a **match** (Strong Fit [80–100] or Moderate Fit [60–79], and no hard dealbreakers/vetoes): **Do not pause or prompt for user approval.** Output the evaluation summary and immediately proceed straight through Step 2 (Drafting), Step 3 (Reviewing), Step 4 (Revising), Step 5 (LaTeX Compilation), and Step 6 (ATS & Google Drive Upload).
  - If the job evaluation results in a **mismatch** (Weak Fit [< 60] or any hard dealbreaker veto): Stop and present the reasons, asking: *"This posting appears to be a mismatch (Score: <score>/100, Reason: <reasons>). Would you like me to proceed with drafting the CV and cover letter anyway?"*
```

### 3.2 Workflow Definition Updates
Update the decision gate at the end of Step 1 in:
1. `.agents/skills/apply/SKILL.md`
2. `.claude/commands/apply.md`

Replace:
```markdown
After presenting the evaluation, ask the user:
> "Should I proceed with drafting the CV and cover letter for this role?"

**If the user says no, stop here.** If yes, continue to Step 2.
```

With:
```markdown
Evaluate whether the role is a match:
- **Match (Auto-Proceed):** If the fit is **Strong Fit** (80–100) or **Moderate Fit** (60–79) with **no hard dealbreaker vetoes** (location, authorization, language), **do not pause or prompt for user confirmation**. Output the evaluation summary and immediately proceed to Step 2: DRAFTER - Draft CV + Cover Letter.
- **Mismatch / Veto (Prompt for Confirmation):** If the fit is **Weak Fit** (< 60) OR trips a hard veto, present the reasons and ask:
  > "This posting appears to be a mismatch (Score: <score>/100, Reason: <reasons>). Would you like me to proceed with drafting the CV and cover letter anyway?"
  If the user says no, stop here. If yes, continue to Step 2.
```

---

## 4. Verification

1. Run unit test suite: `pytest tests/test_apply_host_check.py tests/test_apply_page_count.py tests/test_apply_records_application.py` to ensure all apply-related tests pass.
2. Run `pytest tests/test_security_guards.py` to confirm workspace security checks pass.
3. Verify that the rule in `.agents/AGENTS.md` is active and loaded.
