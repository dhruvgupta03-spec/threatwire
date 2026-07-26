"""No-install publisher: create the GitHub repo and upload the project via the
GitHub REST API using only the Python standard library (no git, gh, or Xcode).

Usage:
    GITHUB_TOKEN=<your-token> ./.venv/bin/python publish.py <github-username>

The token needs permission to create repositories and write repository contents
(classic token: "repo" scope; fine-grained: Administration + Contents: Read/Write,
plus Pages: Read/Write to auto-enable hosting). You can revoke it right after.
"""
from __future__ import annotations

import base64
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

import certifi

# macOS Python.org builds lack root CA certs; point urllib at certifi's bundle
# so HTTPS calls to the GitHub API verify correctly.
_SSL_CTX = ssl.create_default_context(cafile=certifi.where())

API = "https://api.github.com"
REPO = "threatwire"
ROOT = Path(__file__).resolve().parent

# What to publish (source only — the site/ output is built by GitHub Actions).
INCLUDE_DIRS = ["src", "templates", "static", ".github"]
INCLUDE_FILES = ["requirements.txt", "README.md", ".gitignore", "deploy.sh", "publish.py"]
SKIP_PARTS = {".venv", "site", "data", "__pycache__", ".git"}
SKIP_SUFFIX = {".pyc"}


def api(method: str, path: str, token: str, body: dict | None = None) -> tuple[int, dict]:
    url = path if path.startswith("http") else f"{API}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "threatwire-publisher")
    try:
        with urllib.request.urlopen(req, context=_SSL_CTX) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"message": raw}


def collect_files() -> list[Path]:
    files: list[Path] = []
    for d in INCLUDE_DIRS:
        for p in (ROOT / d).rglob("*"):
            if p.is_file() and not (SKIP_PARTS & set(p.parts)) and p.suffix not in SKIP_SUFFIX:
                files.append(p)
    for f in INCLUDE_FILES:
        if (ROOT / f).is_file():
            files.append(ROOT / f)
    return files


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("ERROR: set GITHUB_TOKEN env var to your Personal Access Token.", file=sys.stderr)
        return 2
    # 1. Verify the token & identity.
    status, me = api("GET", "/user", token)
    if status != 200:
        print(f"ERROR: token check failed ({status}): {me.get('message')}", file=sys.stderr)
        return 1

    # Username: use the arg if given, else auto-detect from the token.
    user = sys.argv[1].strip() if len(sys.argv) > 1 else me.get("login", "")
    if not user:
        print("ERROR: could not determine username.", file=sys.stderr)
        return 1
    print(f"Authenticated as: {me.get('login')} — publishing to {user}/{REPO}")

    # 2. Create the repo (ignore 'already exists').
    status, resp = api("POST", "/user/repos", token, {
        "name": REPO, "private": False,
        "description": "Proactive threat-intelligence front page, updated on the loop.",
        "homepage": f"https://{user}.github.io/{REPO}/",
    })
    if status in (200, 201):
        print(f"Created repo {user}/{REPO}")
    elif status == 422:
        print(f"Repo {user}/{REPO} already exists — updating files.")
    else:
        print(f"ERROR creating repo ({status}): {resp.get('message')}", file=sys.stderr)
        return 1

    # 3. Upload every file (create or update).
    files = collect_files()
    print(f"Publishing {len(files)} files...")
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        content = base64.b64encode(p.read_bytes()).decode()
        # Existing file? fetch sha so we update instead of failing.
        st, cur = api("GET", f"/repos/{user}/{REPO}/contents/{rel}", token)
        body = {"message": f"Publish {rel}", "content": content}
        if st == 200 and isinstance(cur, dict) and cur.get("sha"):
            body["sha"] = cur["sha"]
        st, r = api("PUT", f"/repos/{user}/{REPO}/contents/{rel}", token, body)
        mark = "✓" if st in (200, 201) else f"✗ {st}"
        print(f"  {mark} {rel}" + ("" if st in (200, 201) else f" — {r.get('message')}"))

    # 4. Enable GitHub Pages (Actions build).
    st, r = api("POST", f"/repos/{user}/{REPO}/pages", token, {"build_type": "workflow"})
    if st in (201, 204):
        print("Enabled GitHub Pages (Actions build).")
    elif st == 409:
        print("GitHub Pages already enabled.")
    else:
        print(f"Note: enable Pages manually if needed (Settings → Pages → Source: GitHub Actions). [{st}] {r.get('message')}")

    print("\nDone.")
    print(f"  Actions:   https://github.com/{user}/{REPO}/actions")
    print(f"  Live site: https://{user}.github.io/{REPO}/  (after the first build, ~1-2 min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
