#!/bin/bash
set -euo pipefail

SRC="aifx/"
DEV_DEST="/opt/dev/aifx/aifx/lib/python3.11/site-packages/aifx/"

mkdir -p "$DEV_DEST"

rsync -avr --delete "$SRC" "$DEV_DEST" | grep -v __pycache__
