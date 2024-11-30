#!/bin/bash

# Cleanup script for removing temporary and unnecessary files

echo "Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -r {} +

# Remove SQLite database
echo "Removing SQLite database..."
rm -f db.sqlite3

# Remove log files
echo "Removing log files..."
rm -f logs/*.log

# Remove virtual environment
echo "Removing virtual environment..."
rm -rf venv/

# Remove coverage and build files
echo "Removing coverage and build files..."
rm -rf htmlcov/ .coverage dist/ build/ *.egg-info
