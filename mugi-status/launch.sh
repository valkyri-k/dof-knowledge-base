#!/usr/bin/env bash
# Idempotent launcher for mugi-status HTTP endpoint.
# Spawns a detached tmux session running status.py on PORT (default 8080).
# Safe to re-run: exits early if the session is already alive.

set -euo pipefail

SESSION="mugi-status"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="${SCRIPT_DIR}/status.py"
LOG="${SCRIPT_DIR}/status.log"

if ! command -v tmux >/dev/null 2>&1; then
  echo "error: tmux not installed in container" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 not installed in container" >&2
  exit 1
fi

if tmux has-session -t "${SESSION}" 2>/dev/null; then
  echo "mugi-status: tmux session '${SESSION}' already running."
  echo "  attach:  tmux attach -t ${SESSION}"
  echo "  tail:    tail -f ${LOG}"
  echo "  kill:    tmux kill-session -t ${SESSION}"
  exit 0
fi

PORT="${PORT:-8080}"
export PORT
export MUGI_STATUS_TOKEN="${MUGI_STATUS_TOKEN:-}"

tmux new-session -d -s "${SESSION}" \
  "python3 -u '${SCRIPT}' 2>&1 | tee -a '${LOG}'"

sleep 1
if tmux has-session -t "${SESSION}" 2>/dev/null; then
  echo "mugi-status: spawned in tmux session '${SESSION}' on :${PORT}"
  echo "  health:  curl -s http://127.0.0.1:${PORT}/health"
  echo "  tail:    tail -f ${LOG}"
else
  echo "error: tmux session failed to start. Check ${LOG}" >&2
  exit 1
fi
