#!/usr/bin/env bash
# BRAVIA Control Center — Quick Launch Script
echo "============================================================"
echo "🚀 Launching BRAVIA Control Center v3.0 Ultra..."
echo "============================================================"

# Ensure adb is accessible
if ! command -v adb &> /dev/null; then
    if [ -f "/opt/homebrew/bin/adb" ]; then
        export PATH="/opt/homebrew/bin:$PATH"
    fi
fi

# Kill any existing server on port 8888
lsof -ti:8888 | xargs kill -9 2>/dev/null || true
sleep 1

# Launch Python backend server
python3 dashboard.py
