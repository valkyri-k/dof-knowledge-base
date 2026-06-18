#!/usr/bin/env python3
"""
get-youtube-token.py — one-time: obtain a youtube.readonly OAuth refresh token
for the DOF dofofapple@gmail.com channel, used by scripts/youtube-search.js.

Reuses the existing dofofapple OAuth client (~/.credentials/youtube/client_secret.json,
GCP project youtube-api-492515). Opens a browser for consent — you MUST log in as
dofofapple@gmail.com (NOT karyto.dof). Writes the refresh token to
~/.credentials/youtube/mugi-readonly-token.txt (chmod 600). Does NOT print the
token to stdout, to avoid leaking it into logs/chat.

Usage: python3 scripts/get-youtube-token.py
Then: open that file, copy value into Zeabur YOUTUBE_REFRESH_TOKEN.
"""
import os
import stat

from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRET = os.path.expanduser("~/.credentials/youtube/client_secret.json")
OUT = os.path.expanduser("~/.credentials/youtube/mugi-readonly-token.txt")
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


def main():
    if not os.path.exists(CLIENT_SECRET):
        raise SystemExit(f"Missing {CLIENT_SECRET}")
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    if not creds.refresh_token:
        raise SystemExit("No refresh token returned. Re-run; ensure prompt=consent.")
    with open(OUT, "w") as f:
        f.write(creds.refresh_token)
    os.chmod(OUT, stat.S_IRUSR | stat.S_IWUSR)
    print(f"\n✅ Refresh token written to {OUT} (chmod 600).")
    print("Open that file, copy the value into Zeabur YOUTUBE_REFRESH_TOKEN.")
    print("It is NOT printed here, to avoid leaking into logs.")


if __name__ == "__main__":
    main()
