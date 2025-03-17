#!/bin/bash

# Ensure the script runs from the repo root
cd "$(dirname "$0")"

# Ensure bin/ exists
mkdir -p bin

# Grant execute permission to all Python files in bin/
chmod +x bin/*.py

# Fix line endings for Python scripts in bin/
sed -i 's/\r$//' bin/*.py 2>/dev/null || true

echo "Setup complete! Python scripts in bin/ are now executable."
