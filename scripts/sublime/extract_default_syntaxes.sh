#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# SRC_DIR="/opt/sublime_text/Packages"
# DEST_DIR="./default_syntaxes"
DEST_DIR="./external_syntaxes"
SRC_DIR="/home/betehe/.config/sublime-text/Installed Packages/"

# Ensure the destination directory exists
mkdir -p "$DEST_DIR"

echo "Scanning for Sublime Text syntax files..."

# Check if the source directory exists
if [ ! -d "$SRC_DIR" ]; then
    echo "Error: Source directory $SRC_DIR not found." >&2
    exit 1
fi

# Loop through all .sublime-package files
for pkg in "$SRC_DIR"/*.sublime-package; do
    [ -e "$pkg" ] || continue
    
    pkg_name=$(basename "$pkg")
    extracted=0

    # Extract each pattern separately to avoid unzip erroring on missing patterns
    for pattern in "*.sublime-syntax" "*.tmLanguage"; do
        if unzip -l "$pkg" "$pattern" > /dev/null 2>&1; then
            if [ $extracted -eq 0 ]; then
                echo "Extracting from $pkg_name..."
                extracted=1
            fi
            unzip -j -o "$pkg" "$pattern" -d "$DEST_DIR" > /dev/null
        fi
    done
done

echo "Done! Syntaxes extracted to $DEST_DIR"