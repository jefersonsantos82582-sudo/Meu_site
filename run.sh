#!/usr/bin/env bash
# Sobe o backend Python (que já serve o frontend JavaScript).
set -e
cd "$(dirname "$0")/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  ./.venv/bin/pip install -q --upgrade pip
  ./.venv/bin/pip install -q -r requirements.txt
fi
exec ./.venv/bin/uvicorn main:app --reload --port 8000
