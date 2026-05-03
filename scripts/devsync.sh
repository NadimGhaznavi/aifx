#!/bin/bash -x
set -euo pipefail

SRC="/opt/dev/aifx/aifx/"
DEV_DEST="/opt/dev/aifx/aifx_venv/lib/python3.11/site-packages/aifx/"

mkdir -p "$DEV_DEST"

rsync -avr --delete \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  "$SRC" "$DEV_DEST"
