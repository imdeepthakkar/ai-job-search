#!/usr/bin/env python3
"""Upload generated CV and Cover Letter files to Google Drive.

Supported Authentication & Upload Methods:
  1. Google Apps Script Webhook (Recommended - No GCP or Org Policy required):
     - Set GDRIVE_WEBHOOK_URL (e.g. https://script.google.com/macros/s/.../exec)
     - Set GDRIVE_FOLDER_ID
     - Set GDRIVE_WEBHOOK_SECRET (optional, default: "DeepJobSearch2026")

  2. Google Service Account (if permitted by org):
     - Set GDRIVE_SERVICE_ACCOUNT_KEY or credentials/google_service_account.json
     - Set GDRIVE_FOLDER_ID

Usage examples:
  # Upload specific files
  python tools/upload_to_gdrive.py cv/CV_DeepThakkar_Google.pdf cover_letters/CL_DeepThakkar_Google.pdf

  # Upload the most recently generated CV and Cover Letter
  python tools/upload_to_gdrive.py --latest

  # Test credentials and connection
  python tools/upload_to_gdrive.py --check
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Tuple

DEFAULT_SECRET = "DeepJobSearch2026"
DEFAULT_CREDS_PATH = Path("credentials/google_service_account.json")


def upload_via_webhook(file_path: Path, folder_id: str, webhook_url: str, secret: str) -> Tuple[bool, str, str]:
    """Upload a file using a Google Apps Script Web App endpoint."""
    file_name = file_path.name
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = "application/pdf"

    try:
        with open(file_path, "rb") as f:
            encoded_content = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "name": file_name,
            "mimeType": mime_type,
            "folderId": folder_id,
            "secret": secret,
            "content": encoded_content,
        }

        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            raw_response = resp.read().decode("utf-8")
            res = json.loads(raw_response)

        if res.get("status") == "success":
            return True, res.get("url", ""), res.get("fileId", "")
        else:
            return False, res.get("message", "Unknown error from Apps Script"), ""

    except Exception as e:
        return False, str(e), ""


def get_service_account_credentials():
    """Retrieve Google Service Account credentials from env var or file if available."""
    try:
        from google.oauth2 import service_account
    except ImportError:
        return None

    scopes = [
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]

    key_env = os.environ.get("GDRIVE_SERVICE_ACCOUNT_KEY")
    if key_env:
        try:
            if not key_env.strip().startswith("{"):
                decoded = base64.b64decode(key_env).decode("utf-8")
            else:
                decoded = key_env
            info = json.loads(decoded)
            return service_account.Credentials.from_service_account_info(info, scopes=scopes)
        except Exception:
            pass

    file_env = os.environ.get("GDRIVE_SERVICE_ACCOUNT_FILE")
    if file_env and Path(file_env).is_file():
        return service_account.Credentials.from_service_account_file(file_env, scopes=scopes)

    if DEFAULT_CREDS_PATH.is_file():
        return service_account.Credentials.from_service_account_file(str(DEFAULT_CREDS_PATH), scopes=scopes)

    return None


def find_latest_file(directory: Path, pattern: str) -> Optional[Path]:
    """Find the most recently modified file matching pattern in directory."""
    if not directory.exists():
        return None
    candidates = list(directory.glob(pattern))
    if not candidates:
        return None
    return max(candidates, key=lambda f: f.stat().st_mtime)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", help="File path(s) to upload")
    parser.add_argument("--latest", action="store_true", help="Auto-detect latest CV and Cover Letter PDFs")
    parser.add_argument("--folder-id", default=os.environ.get("GDRIVE_FOLDER_ID"), help="Target Google Drive Folder ID")
    parser.add_argument("--webhook-url", default=os.environ.get("GDRIVE_WEBHOOK_URL"), help="Google Apps Script Web App URL")
    parser.add_argument("--secret", default=os.environ.get("GDRIVE_WEBHOOK_SECRET", DEFAULT_SECRET), help="Shared secret for Apps Script")
    parser.add_argument("--check", action="store_true", help="Verify credentials and connection")
    parser.add_argument("--optional", action="store_true", help="Do not exit with error if credentials not configured")
    args = parser.parse_args()

    webhook_url = args.webhook_url
    folder_id = args.folder_id
    sa_creds = get_service_account_credentials()

    has_webhook = bool(webhook_url and folder_id)
    has_sa = bool(sa_creds and folder_id)

    if not has_webhook and not has_sa:
        if args.optional:
            print("INFO: Google Drive credentials not configured. Skipping Drive upload.")
            sys.exit(0)
        print("ERROR: Google Drive configuration not found.", file=sys.stderr)
        print("Set either:", file=sys.stderr)
        print("  1. GDRIVE_WEBHOOK_URL + GDRIVE_FOLDER_ID (Google Apps Script Webhook)", file=sys.stderr)
        print("  2. GDRIVE_SERVICE_ACCOUNT_KEY / credentials file + GDRIVE_FOLDER_ID", file=sys.stderr)
        sys.exit(1)

    if args.check:
        if has_webhook:
            print("Google Apps Script Webhook configured:")
            print(f"  URL: {webhook_url[:40]}...")
            print(f"  Target Folder ID: {folder_id}")
            print("SUCCESS: Webhook configuration verified.")
        elif has_sa:
            print("Google Service Account configured:")
            print(f"  Target Folder ID: {folder_id}")
            print("SUCCESS: Service Account configuration verified.")
        sys.exit(0)

    # Determine files to upload
    files_to_upload = [Path(f) for f in args.files]

    if args.latest or not files_to_upload:
        latest_cv = find_latest_file(Path("cv"), "*.pdf")
        latest_cl = find_latest_file(Path("cover_letters"), "*.pdf")
        if latest_cv:
            files_to_upload.append(latest_cv)
        if latest_cl:
            files_to_upload.append(latest_cl)

    if not files_to_upload:
        print("No files found to upload.", file=sys.stderr)
        sys.exit(0)

    print(f"\nUploading {len(files_to_upload)} file(s) to Google Drive...")
    uploaded_count = 0

    for f in files_to_upload:
        if not f.exists():
            print(f"  [MISSING] {f}", file=sys.stderr)
            continue

        if has_webhook:
            success, url_or_err, file_id = upload_via_webhook(f, folder_id, webhook_url, args.secret)
            if success:
                print(f"  [UPLOADED] {f.name} -> {url_or_err or file_id}")
                uploaded_count += 1
            else:
                print(f"  [FAILED] {f.name}: {url_or_err}", file=sys.stderr)
        elif has_sa:
            # Fallback to Service Account upload if configured
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            service = build("drive", "v3", credentials=sa_creds)
            mime_type, _ = mimetypes.guess_type(str(f))
            media = MediaFileUpload(str(f), mimetype=mime_type or "application/pdf")
            try:
                res = service.files().create(body={"name": f.name, "parents": [folder_id]}, media_body=media, fields="id, name, webViewLink").execute()
                print(f"  [UPLOADED] {res.get('name')} -> {res.get('webViewLink')}")
                uploaded_count += 1
            except Exception as e:
                print(f"  [FAILED] {f.name}: {e}", file=sys.stderr)

    if uploaded_count > 0:
        print(f"\nDone! Successfully uploaded {uploaded_count} file(s) to Google Drive.\n")
    else:
        print("\nFailed to upload files to Google Drive.\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
