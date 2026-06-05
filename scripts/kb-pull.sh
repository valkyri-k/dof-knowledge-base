#!/usr/bin/env bash
# kb-pull.sh — safe deploy-pull for the Mugi KB container.
#
# WHY THIS EXISTS
# Mugi appends activity logs immediately but defers `git push` to pre-clear /
# daily cron (schema rule). So between pre-clears the container working tree
# ALWAYS has uncommitted activity writes. A plain `git pull` onto that dirty
# tree forces a stash → pull → pop; if the pulled commits also touched activity
# files, the pop conflicts and leaves an ORPHAN STASH + conflict markers behind.
# 12 such orphans accumulated over May 2026 from ad-hoc `git stash && git pull
# && git stash pop` deploys.
#
# THE FIX
# Commit pending runtime writes FIRST, so the tree is clean at pull time. A
# clean-tree `git pull --rebase` is a fast-forward or a clean rebase — never a
# stash, never a pop, never an orphan. Push batching intent is preserved at the
# semantic level (this only runs on deploy, not per-event).
#
# USAGE (from host, via Zeabur exec):
#   echo "" | $ZEABUR service exec --name claude-code -i=false -- \
#     bash -c 'bash /home/node/kb/scripts/kb-pull.sh'
# Or inside the container:  bash /home/node/kb/scripts/kb-pull.sh
#
# NEVER deploy with `git stash && git pull && git stash pop` again — that is the
# exact pattern that caused the orphan-stash pileup.

set -euo pipefail
export GIT_PAGER=cat PAGER=cat

REPO="${KB_REPO:-/home/node/kb}"
cd "$REPO"

# 1. Commit any pending working-tree changes (Mugi's between-pre-clear activity
#    writes, runtime logs, etc.) so the pull sees a clean tree.
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  git add -A
  git commit -q -m "chore: autosave runtime state before pull"
  echo "kb-pull: committed pending working-tree changes."
else
  echo "kb-pull: working tree already clean."
fi

# 2. Rebase-pull onto the clean tree. No --autostash (autostash re-introduces the
#    pop-conflict / orphan-stash failure mode this script exists to prevent).
git pull --rebase --no-edit origin main

# 3. Push so the container and origin stay in sync (prevents the next pull from
#    being a divergent rebase, and backs the autosaved activity up to GitHub).
git push origin HEAD:main

echo "kb-pull: synced — now at $(git --no-pager log --oneline -1)"
