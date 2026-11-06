#!/usr/bin/env bash
# FestCommand Quick Setup
# =======================
# Sets up FestCommand for local testing with Switch.
#
# Prerequisites:
#   - Switch Core running (just run)
#   - Switch Console installed
#   - Python 3.10+ (for rehearsal script)
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🎮 FestCommand Setup"
echo "===================="
echo ""

# Check Python
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

echo "✓ Python: $($PYTHON --version)"

# Validate template
echo ""
echo "📋 Validating template..."
if [ -f "$PROJECT_DIR/festcommand.template.yaml" ]; then
    echo "✓ festcommand.template.yaml found"
else
    echo "❌ festcommand.template.yaml not found!"
    exit 1
fi

# Check documents
echo ""
echo "📄 Checking documents..."
for doc in schedule_and_rules.md bracket_state.json sponsor_ledger.json; do
    if [ -f "$PROJECT_DIR/documents/$doc" ]; then
        echo "✓ documents/$doc"
    else
        echo "❌ documents/$doc missing!"
        exit 1
    fi
done

# Check agent skills
echo ""
echo "🤖 Checking agent skills..."
for agent in concierge bracket-marshal sponsor-tracker; do
    if [ -f "$PROJECT_DIR/agents/$agent/SKILL.md" ]; then
        echo "✓ agents/$agent/SKILL.md"
    else
        echo "❌ agents/$agent/SKILL.md missing!"
        exit 1
    fi
done

echo ""
echo "══════════════════════════════════════════"
echo "✅ All files validated!"
echo ""
echo "Next steps:"
echo "  1. Run the rehearsal:  $PYTHON scripts/rehearse.py"
echo "  2. Import into Switch: Open Switch Console → Import Template"
echo "     → Select festcommand.template.yaml"
echo "  3. Configure: Set fest name, choose Discord/Slack bridge"
echo "  4. Launch: Click 'Create Rooms' in Switch Console"
echo "══════════════════════════════════════════"
