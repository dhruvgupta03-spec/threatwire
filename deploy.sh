#!/usr/bin/env bash
# One-shot deploy: create the GitHub repo, push, and turn on Pages (Actions build).
# Prereqs: git + gh installed, and `gh auth login` completed.
#
#   ./deploy.sh <github-username>
#
set -euo pipefail

USER="${1:?Usage: ./deploy.sh <github-username>}"
REPO="threatwire"

command -v git >/dev/null || { echo "git not installed"; exit 1; }
command -v gh  >/dev/null || { echo "gh (GitHub CLI) not installed"; exit 1; }

# 1. Make sure we're authenticated.
gh auth status >/dev/null 2>&1 || gh auth login

# 2. Initialize the local repo (idempotent).
if [ ! -d .git ]; then
  git init -b main
fi
git add -A
git commit -m "ThreatWire: threat-intel front page + per-story briefs" || echo "(nothing new to commit)"

# 3. Create the remote repo and push (idempotent-ish).
if gh repo view "$USER/$REPO" >/dev/null 2>&1; then
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$USER/$REPO.git"
  git push -u origin main
else
  gh repo create "$USER/$REPO" --public --source=. --remote=origin --push
fi

# 4. Enable GitHub Pages with the GitHub Actions build type.
gh api --method POST "repos/$USER/$REPO/pages" -f build_type=workflow 2>/dev/null \
  || echo "(Pages already enabled or will be set via Settings → Pages → Source: GitHub Actions)"

echo ""
echo "Done. First build runs now. Watch it at:"
echo "  https://github.com/$USER/$REPO/actions"
echo "Live site (after ~1-2 min):"
echo "  https://$USER.github.io/$REPO/"
