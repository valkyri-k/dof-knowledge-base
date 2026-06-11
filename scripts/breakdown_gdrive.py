#!/usr/bin/env python3
"""
Google Drive I/O for Mugi director video-shot-breakdown skill.

Single source of truth for Drive download (source video) + upload (output xlsx).
Authenticates as dof.internal@gmail.com via the GOOGLE_DRIVE_* refresh-token
OAuth set already on the container. Importable by breakdown_extract.py /
breakdown_render.py, and runnable as a CLI for verification.

Usage (CLI):
  python3 scripts/breakdown_gdrive.py whoami
  python3 scripts/breakdown_gdrive.py download <drive-url-or-id> <dest-path>
  python3 scripts/breakdown_gdrive.py upload <local-path> [parent-folder-id]
  python3 scripts/breakdown_gdrive.py roundtrip          # self-test, no external file

Output: single line JSON to stdout. On error: {"status":"error","error":...},
exit code 0 (caller parses status field). Never prints secret values.

Env required: GOOGLE_DRIVE_CLIENT_ID, GOOGLE_DRIVE_CLIENT_SECRET,
GOOGLE_DRIVE_REFRESH_TOKEN. Optional: GOOGLE_DRIVE_DOCGEN_FOLDER_ID (default
upload parent).
"""

import argparse
import io
import json
import os
import re
import sys

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaInMemoryUpload

TOKEN_URI = "https://oauth2.googleapis.com/token"


def get_drive_service():
    """Build an authenticated Drive v3 service as dof.internal via refresh token."""
    creds = Credentials(
        None,
        refresh_token=os.environ["GOOGLE_DRIVE_REFRESH_TOKEN"],
        client_id=os.environ["GOOGLE_DRIVE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_DRIVE_CLIENT_SECRET"],
        token_uri=TOKEN_URI,
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def extract_drive_id(url_or_id):
    """Pull a Drive file ID out of any common share-URL form, or pass through a bare ID.

    Handles:
      https://drive.google.com/file/d/<ID>/view
      https://drive.google.com/open?id=<ID>
      https://drive.google.com/uc?id=<ID>&export=download
      https://docs.google.com/document/d/<ID>/edit
      <ID>
    """
    s = url_or_id.strip()
    if "drive.google.com" not in s and "docs.google.com" not in s:
        return s  # assume already a bare ID
    m = re.search(r"/d/([A-Za-z0-9_-]+)", s)
    if m:
        return m.group(1)
    m = re.search(r"[?&]id=([A-Za-z0-9_-]+)", s)
    if m:
        return m.group(1)
    raise ValueError(f"Cannot extract Drive file ID from: {s}")


def download_drive(url_or_id, dest_path, service=None):
    """Download a Drive file (binary) to dest_path. Returns dict with name/mime/size."""
    service = service or get_drive_service()
    file_id = extract_drive_id(url_or_id)
    meta = service.files().get(
        fileId=file_id, fields="id,name,mimeType,size", supportsAllDrives=True
    ).execute()
    request = service.files().get_media(fileId=file_id)
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    with io.FileIO(dest_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request, chunksize=8 * 1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    return {
        "id": file_id,
        "name": meta.get("name"),
        "mime": meta.get("mimeType"),
        "size": meta.get("size"),
        "path": os.path.abspath(dest_path),
    }


FOLDER_MIME = "application/vnd.google-apps.folder"


def create_folder(name, parent_id=None, service=None):
    """Create a Drive folder under parent_id (default = docgen folder). Returns id + link."""
    service = service or get_drive_service()
    parent_id = parent_id or os.environ.get("GOOGLE_DRIVE_DOCGEN_FOLDER_ID")
    body = {"name": name, "mimeType": FOLDER_MIME}
    if parent_id:
        body["parents"] = [parent_id]
    created = service.files().create(
        body=body, fields="id,name,webViewLink", supportsAllDrives=True,
    ).execute()
    return {
        "id": created["id"],
        "name": created.get("name"),
        "link": created.get("webViewLink"),
    }


def set_anyone_writer(file_id, service=None):
    """Grant 'anyone with the link can EDIT' on a file or folder.

    Applied to the per-job folder so xlsx + strips + frames + contact sheet are
    all link-editable in one call (folder permission cascades to children).
    dof.internal is a consumer @gmail account, so type=anyone sharing is allowed.
    Returns the permission id + role for caller confirmation.
    """
    service = service or get_drive_service()
    created = service.permissions().create(
        fileId=file_id,
        body={"role": "writer", "type": "anyone"},
        supportsAllDrives=True,
        fields="id,role,type",
    ).execute()
    return {"id": created.get("id"), "role": created.get("role"), "type": created.get("type")}


def upload_file(local_path, parent_id=None, name=None, service=None):
    """Upload a local file to a Drive folder. Returns dict with id + webViewLink."""
    service = service or get_drive_service()
    parent_id = parent_id or os.environ.get("GOOGLE_DRIVE_DOCGEN_FOLDER_ID")
    name = name or os.path.basename(local_path)
    body = {"name": name}
    if parent_id:
        body["parents"] = [parent_id]
    media = MediaFileUpload(local_path, resumable=True)
    created = service.files().create(
        body=body, media_body=media,
        fields="id,name,webViewLink", supportsAllDrives=True,
    ).execute()
    return {
        "id": created["id"],
        "name": created.get("name"),
        "link": created.get("webViewLink"),
    }


# ---------- CLI ----------

def _emit(obj):
    print(json.dumps(obj, ensure_ascii=False))


def _cli():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("whoami")
    d = sub.add_parser("download")
    d.add_argument("url_or_id")
    d.add_argument("dest")
    u = sub.add_parser("upload")
    u.add_argument("path")
    u.add_argument("parent", nargs="?", default=None)
    mk = sub.add_parser("mkfolder")
    mk.add_argument("name")
    mk.add_argument("parent", nargs="?", default=None)
    sh = sub.add_parser("share")
    sh.add_argument("file_id")
    sub.add_parser("roundtrip")
    args = ap.parse_args()

    svc = get_drive_service()

    if args.cmd == "whoami":
        about = svc.about().get(fields="user(emailAddress,displayName)").execute()
        out = {"status": "ok", "email": about["user"]["emailAddress"]}
        folder = os.environ.get("GOOGLE_DRIVE_DOCGEN_FOLDER_ID")
        if folder:
            fm = svc.files().get(fileId=folder, fields="id,name",
                                 supportsAllDrives=True).execute()
            out["docgen_folder"] = fm.get("name")
        _emit(out)

    elif args.cmd == "download":
        r = download_drive(args.url_or_id, args.dest, service=svc)
        _emit({"status": "ok", **r})

    elif args.cmd == "upload":
        r = upload_file(args.path, parent_id=args.parent, service=svc)
        _emit({"status": "ok", **r})

    elif args.cmd == "mkfolder":
        r = create_folder(args.name, parent_id=args.parent, service=svc)
        _emit({"status": "ok", **r})

    elif args.cmd == "share":
        r = set_anyone_writer(args.file_id, service=svc)
        _emit({"status": "ok", **r})

    elif args.cmd == "roundtrip":
        # Self-test: create folder -> upload tiny file into it -> download back ->
        # verify -> delete folder (recursive). Exercises mkfolder + nested upload.
        parent = os.environ.get("GOOGLE_DRIVE_DOCGEN_FOLDER_ID")
        folder = create_folder("_breakdown_gdrive_roundtrip", parent_id=parent, service=svc)
        payload = b"breakdown-gdrive-roundtrip"
        media = MediaInMemoryUpload(payload, mimetype="text/plain")
        created = svc.files().create(
            body={"name": "probe.txt", "parents": [folder["id"]]},
            media_body=media, fields="id", supportsAllDrives=True).execute()
        got = svc.files().get_media(fileId=created["id"]).execute()
        ok = got == payload
        # Deleting the folder removes its children too.
        svc.files().delete(fileId=folder["id"], supportsAllDrives=True).execute()
        _emit({"status": "ok", "roundtrip": ok, "folder_id": folder["id"]})


if __name__ == "__main__":
    try:
        _cli()
    except Exception as e:  # noqa: BLE001 - CLI surfaces all errors as JSON
        _emit({"status": "error", "error": f"{type(e).__name__}: {e}"})
