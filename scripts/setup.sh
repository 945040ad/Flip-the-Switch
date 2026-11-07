#!/usr/bin/env bash
# FestCommand setup check
# =======================
# Verifies everything needed to rehearse locally and to import the template
# into Switch:
#   1. Python 3.10+ is available (PyYAML optional, enables deeper template checks)
#   2. festcommand.template.yaml was built from the current sources
#   3. The template, the three room documents and the rulebook agree
#      with each other (scripts/validate.py)
#   4. The validator still catches every class of mistake it claims to
#      (tests/, mutation tests on a throwaway copy)
#
# Usage:  ./scripts/setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "🎮 FestCommand setup check"
echo "=========================="

PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "❌ Python 3.10+ not found. Install it from https://www.python.org/downloads/"
    exit 1
fi
echo "✓ $($PYTHON --version)"

if "$PYTHON" -c 'import yaml' 2>/dev/null; then
    echo "✓ PyYAML available (structural template checks enabled)"
else
    echo "⚠ PyYAML not installed; template structure checks will be skipped."
    echo "  Enable them with:  $PYTHON -m pip install pyyaml"
fi

echo ""
"$PYTHON" scripts/validate.py

echo ""
echo "── Mutation tests"
if ! TESTS="$("$PYTHON" -m unittest discover -s tests 2>&1)"; then
    echo "$TESTS"
    exit 1
fi
echo "$TESTS" | tail -n 1
if echo "$TESTS" | grep -q "skipped="; then
    echo "  (template tests skipped: install PyYAML to run them)"
fi

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "Next steps"
echo "  1. Rehearse locally:   $PYTHON scripts/rehearse.py   (add --fast to skip pauses)"
echo "  2. Deploy on Switch:   Switch Console → Templates → import festcommand.template.yaml"
echo "                         set the fest name and messaging app, then create."
echo "  3. After editing agents/ or documents/, rebuild the template:"
echo "                         $PYTHON scripts/build_template.py"
echo "══════════════════════════════════════════════════════════════"
