# Workspace Rules

- **Non-Interactive Build Mode**: Always run LaTeX compilers (e.g., `xelatex`, `lualatex`, `pdflatex`) in non-interactive mode using the `-interaction=nonstopmode` flag to prevent terminal compilation hanging on warnings or errors.
- **CV Filename Convention**: Generated resume/CV files must follow the naming pattern `cv/CV_DeepThakkar_<CompanyName>.pdf` (and `.tex`).
- **Cover Letter Filename Convention**: Generated cover letter files must follow the naming pattern `cover_letters/CL_DeepThakkar_<CompanyName>.pdf` (and `.tex`).
- **Google Drive Backup**: After generating and compiling the CV and cover letter PDFs, automatically run `python tools/upload_to_gdrive.py --latest --optional` to back them up to Google Drive.
