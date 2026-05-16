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

# Project name
AI_FX="aifx"

# Source the functions file
FUNCTIONS="test_functions.sh"
SCRIPTS_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd -- "$SCRIPTS_DIR/.." && pwd)"

current_version() {
	grep 'VERSION: Final\[str\]' "$BASE_DIR/aifx/constants/DDef.py" |
		sed 's/.*"\([^"]*\)".*/\1/'
}

print_help() {
	echo "Usage: $0 run"
	echo ""
	echo "Runs the final pre-release checks for $AI_FX."
	echo ""
	echo "Commands:"
	echo "  run      Execute the final test suite"
	echo "  -h       Show this help"
	echo "  --help   Show this help"
}

if [ -e "$SCRIPTS_DIR/$FUNCTIONS" ]; then
	source "$SCRIPTS_DIR/$FUNCTIONS"
else
	echo "FATAL ERROR: Unable to find functions file: $SCRIPTS_DIR/$FUNCTIONS"
	exit 1
fi

cd "$BASE_DIR"

if [ $# -eq 0 ]; then
	echo "Current version: $(current_version)"
	echo $DIV
	print_help
	exit 0
fi

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
	echo "Current version: $(current_version)"
	echo $DIV
	print_help
	exit 0
fi

if [[ "$1" != "run" ]]; then
	echo "ERROR: Unknown command: $1"
	echo $DIV
	print_help
	exit 1
fi

# Clear the terminal
clear

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

#echo "🔒 Running bandit security check..."
#bandit -r $AI_FX #--skip B101

echo "🧹 Executing: poetry run pytest..."
poetry run pytest
echo $DIV

#echo "🚦 Executing: shfmt -w scripts/..."
#shfmt -d scripts/
#echo $DIV

echo "👽 Executing: poetry run pre-commit run --all-files ..."
poetry run pre-commit run --all-files
echo $DIV

#echo "🗃️ Rebuilding documentation ..."
#cd $BASE_DIR/docs && make clean
#cd $BASE_DIR/docs && make html
#echo $DIV

echo "✅ All code quality checks passed!"
