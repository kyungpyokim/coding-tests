#!/usr/bin/env bash
# TDD Pytest Watcher Script
# Watches for file changes in src/ and tests/ and automatically runs pytest.

set -e

# Change to project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🧪 Starting Pytest Watcher (TDD Auto-Test Mode)..."
echo "📂 Watching: src/ and tests/"
echo "💡 Press Ctrl+C to exit."
echo "----------------------------------------------------"

# Run pytest-watcher through uv
exec uv run pytest-watcher . --now "$@"
