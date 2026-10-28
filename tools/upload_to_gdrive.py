#!/usr/bin/env python3
"""Upload generated CV and Cover Letter files to Google Drive using a Service Account.

Authentication options (checked in order):
  1. Environment variable GDRIVE_SERVICE_ACCOUNT_KEY (raw JSON or base64 encoded string)
  2. Environment variable GDRIVE_SERVICE_ACCOUNT_FILE (path to JSON key file)
  3. Local file credentials/google_service_account.json

Target Folder (checked in order):
  1. Command line flag: --folder-id <ID>
  2. Environment variable: GDRIVE_FOLDER_ID

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
from pathlib import Path
from typing import Optional

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

DEFAULT_CREDS_PATH = Path("credentials/google_service_account.json")


def get_credentials():
    """Retrieve Google Service Account credentials from env var or file."""
    try:
        from google.oauth2 import service_account
    except ImportError:
        print("ERROR: Google client libraries not installed.", file=sys.stderr)
        print("Install with: pip install google-api-python-client google-auth", file=sys.stderr)
        return None

    # 1. Inline JSON / Base64 in environment variable (Ideal for Codespaces / CI)
    key_env = os.environ.get("GDRIVE_SERVICE_ACCOUNT_KEY")
    if key_env:
        try:
            # Check if base64 encoded
            if not key_env.strip().startswith("{"):
                decoded = base64.b64decode(key_env).decode("utf-8")
            else:
                decoded = key_env
            info = json.loads(decoded)
            return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        except Exception as e:
            print(f"ERROR: Failed to parse GDRIVE_SERVICE_ACCOUNT_KEY: {e}", file=sys.stderr)
            return None

    # 2. File path from environment variable
    file_env = os.environ.get("GDRIVE_SERVICE_ACCOUNT_FILE")
    if file_env and Path(file_env).is_file():
        return service_account.Credentials.from_service_account_file(file_env, scopes=SCOPES)

    # 3. Default local credentials file
    if DEFAULT_CREDS_PATH.is_file():
        return service_account.Credentials.from_service_account_file(
            str(DEFAULT_CREDS_PATH), scopes=SCOPES
        )

    return None


def get_drive_service(creds):
    """Build and return the Google Drive API service client."""
    from googleapiclient.discovery import build
    return build("drive", "v3", credentials=creds)


def find_latest_file(directory: Path, pattern: str) -> Optional[Path]:
    """Find the most recently modified file matching pattern in directory."""
    if not directory.exists():
        return None
    candidates = list(directory.glob(pattern))
    if not candidates:
        return None
    return max(candidates, key=lambda f: f.stat().st_mtime)


def get_or_create_subfolder(service, parent_folder_id: Optional[str], folder_name: str) -> Optional[str]:
    """Retrieve or create a subfolder inside parent_folder_id."""
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_folder_id:
        metadata["parents"] = [parent_folder_id]

    folder = service.files().create(body=metadata, fields="id").execute()
    return folder.get("id")


def upload_file(service, file_path: Path, folder_id: Optional[str] = None):
    """Upload or update a file in Google Drive."""
    from googleapiclient.http import MediaFileUpload

    file_name = file_path.name
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = "application/octet-stream"

    # Check if a file with this name already exists in target folder
    query = f"name = '{file_name}' and trashed = false"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
    existing_files = results.get("files", [])

    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)

    if existing_files:
        # Update existing file
        file_id = existing_files[0]["id"]
        updated = service.files().update(
            fileId=file_id,
            media_body=media,
            fields="id, name, webViewLink",
        ).execute()
        return updated, "updated"
    else:
        # Create new file
        body = {"name": file_name}
        if folder_id:
            body["parents"] = [folder_id]
        created = service.files().create(
            body=body,
            media_body=media,
            fields="id, name, webViewLink",
        ).execute()
        return created, "uploaded"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", help="File path(s) to upload")
    parser.add_argument("--latest", action="store_true", help="Auto-detect latest CV and Cover Letter PDFs")
    parser.add_argument("--folder-id", default=os.environ.get("GDRIVE_FOLDER_ID"), help="Target Google Drive Folder ID")
    parser.add_argument("--subfolder", help="Optional subfolder name inside target folder (e.g. company name)")
    parser.add_argument("--check", action="store_true", help="Verify credentials and connection")
    parser.add_argument("--optional", action="store_true", help="Do not exit with error if credentials not configured")
    args = parser.parse_args()

    creds = get_credentials()
    if not creds:
        if args.optional:
            print("INFO: Google Drive credentials not configured. Skipping Drive upload.")
            sys.exit(0)
        print("ERROR: Google Drive credentials not found.", file=sys.stderr)
        print("Set GDRIVE_SERVICE_ACCOUNT_KEY or place credentials/google_service_account.json", file=sys.stderr)
        sys.exit(1)

    try:
        service = get_drive_service(creds)
    except Exception as e:
        print(f"ERROR: Failed to connect to Google Drive API: {e}", file=sys.stderr)
        sys.exit(1)

    if args.check:
        print("SUCCESS: Google Drive API credentials verified successfully!")
        if args.folder_id:
            try:
                folder = service.files().get(fileId=args.folder_id, fields="id, name").execute()
                print(f"Target folder verified: '{folder.get('name')}' (ID: {folder.get('id')})")
            except Exception as e:
                print(f"WARNING: Could not access target folder {args.folder_id}: {e}", file=sys.stderr)
                print("Make sure you shared the Google Drive folder with the Service Account email address!")
        sys.exit(0)

    # Determine files to upload
    files_to_upload = [Path(f) for f in args.files]

    if args.latest or not files_to_upload:
        # Check cv/ and cover_letters/
        latest_cv = find_latest_file(Path("cv"), "*.pdf")
        latest_cl = find_latest_file(Path("cover_letters"), "*.pdf")
        if latest_cv:
            files_to_upload.append(latest_cv)
        if latest_cl:
            files_to_upload.append(latest_cl)

    if not files_to_upload:
        print("No files found to upload.", file=sys.stderr)
        sys.exit(0)

    # Target folder resolution
    target_folder_id = args.folder_id
    if target_folder_id and args.subfolder:
        try:
            target_folder_id = get_or_create_subfolder(service, target_folder_id, args.subfolder)
        except Exception as e:
            print(f"WARNING: Could not create subfolder '{args.subfolder}': {e}", file=sys.stderr)

    uploaded_count = 0
    print(f"\nUploading {len(files_to_upload)} file(s) to Google Drive...")
    for f in files_to_upload:
        if not f.exists():
            print(f"  [MISSING] {f}", file=sys.stderr)
            continue
        try:
            res, action = upload_file(service, f, target_folder_id)
            link = res.get("webViewLink", "")
            print(f"  [{action.upper()}] {res.get('name')} -> {link or res.get('id')}")
            uploaded_count += 1
        except Exception as e:
            print(f"  [FAILED] {f.name}: {e}", file=sys.stderr)
            if "notFound" in str(e) or "access" in str(e).lower():
                print("    Hint: Ensure the Google Drive folder is shared with your Service Account email with 'Editor' permissions.", file=sys.stderr)

    if uploaded_count > 0:
        print(f"\nDone! Successfully {action} {uploaded_count} file(s) to Google Drive.\n")
    else:
        print("\nFailed to upload files to Google Drive.\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
