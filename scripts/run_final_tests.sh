#!/bin/bash
#
# scripts/run_final_tests.sh
#
#    AI FX
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2026 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/aifx
#    Website: https://aifx.osoyalce.com
#    License: GPL 3.0

# Exit on error
set -e

# Clear the terminal
clear

# Project name
AI_FX="aifx"

# Source the functions file
FUNCTIONS="test_functions.sh"
SCRIPTS_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd -- "$SCRIPTS_DIR/.." && pwd)"

if [ -e "$SCRIPTS_DIR/$FUNCTIONS" ]; then
	source "$SCRIPTS_DIR/$FUNCTIONS"
else
	echo "FATAL ERROR: Unable to find functions file: $SCRIPTS_DIR/$FUNCTIONS"
	exit 1
fi

cd "$BASE_DIR"

echo "🔍 Executing pre-release tests..."
echo $DIV

echo "📝 Running flake8..."
flake8 $AI_FX
echo $DIV

echo "🔍 Running mypy..."
mypy $AI_FX
echo $DIV

echo "🎨 Running black ..."
# Don't check the `ui_form.py` file, it's very Qt specific.
black --check --extend-exclude '(^|/)ui_form\.py$' $AI_FX
echo $DIV

echo "📦 Running isort ..."
isort --check-only $AI_FX

echo "🧹 Executing: poetry run pytest..."
poetry run pytest -v
echo $DIV

echo "✅ All code quality checks passed!"
