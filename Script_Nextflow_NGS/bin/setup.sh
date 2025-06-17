#!/bin/bash

# Ensure the script runs from the repo root
cd "$(dirname "$0")"

# Define base directory
BIN_DIR="/home/bioinfo/Nilesh/NGS3_test/Downstream_Upstream_Test/Upstream_pipeline/Script_Nextflow_NGS/bin"

# Grant execute permission to all Python files in bin/
chmod +x "$BIN_DIR"/*

# Fix line endings for Python scripts in bin/
find "$BIN_DIR" -name "*.py" -exec sed -i 's/\r$//' {} \;

echo "Setup complete! Python scripts in bin/ are now executable."
