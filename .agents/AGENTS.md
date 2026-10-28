# Workspace Rules

- **Non-Interactive Build Mode**: Always run LaTeX compilers (e.g., `xelatex`, `lualatex`, `pdflatex`) in non-interactive mode using the `-interaction=nonstopmode` flag to prevent terminal compilation hanging on warnings or errors.
- **CV Filename Convention**: Generated resume/CV files must follow the naming pattern `cv/CV_DeepThakkar_<CompanyName>.pdf` (and `.tex`).
- **Cover Letter Filename Convention**: Generated cover letter files must follow the naming pattern `cover_letters/CL_DeepThakkar_<CompanyName>.pdf` (and `.tex`).
- **Google Drive Backup**: After generating and compiling the CV and cover letter PDFs, automatically run `python tools/upload_to_gdrive.py --latest --optional` to back them up to Google Drive.
- **Autonomous Application Workflow (Auto-Proceed on Match)**: During the `/apply` workflow:
  - If the job evaluation results in a **match** (Strong Fit [80–100] or Moderate Fit [60–79], with no hard dealbreaker vetoes such as location, work authorization, or mandatory language): **Do not pause or prompt the user for confirmation to proceed.** Output the evaluation summary and immediately proceed straight through Step 2 (Drafting), Step 3 (Reviewing), Step 4 (Revising), Step 5 (LaTeX Compilation), and Step 6 (ATS & Google Drive Upload).
  - If the job evaluation results in a **mismatch** (Weak Fit [< 60] or trips a hard dealbreaker veto): Stop and explain the reasons, asking: *"This posting appears to be a mismatch (Score: <score>/100, Reason: <reasons>). Would you like me to proceed with drafting the CV and cover letter anyway?"*
