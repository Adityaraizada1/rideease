#!/usr/bin/env bash
# RideEase GUI Launcher
# Usage:
#   ./run_gui.sh         # Opens the native Desktop GUI application
#   ./run_gui.sh --web   # Launches the web dashboard and opens in browser

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ "$1" == "--web" ] || [ "$1" == "-w" ]; then
    echo "Starting RideEase Web Dashboard on http://localhost:8080..."
    open "http://localhost:8080" 2>/dev/null || true
    python3 web_gui.py 8080
else
    echo "Launching RideEase Desktop GUI..."
    python3 gui.py
fi

