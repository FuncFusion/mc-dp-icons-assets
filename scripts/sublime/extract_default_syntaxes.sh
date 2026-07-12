#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

SRC_DIR="/opt/sublime_text/Packages"
DEST_DIR="./default_syntaxes"

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
    # Check if files actually exist to avoid literal glob matching if empty
    [ -e "$pkg" ] || continue
    
    pkg_name=$(basename "$pkg")
    
    # Check if the package contains any .sublime-syntax files before extracting
    if unzip -l "$pkg" "*.sublime-syntax" > /dev/null 2>&1; then
        echo "Extracting from $pkg_name..."
        # -j junk paths (do not recreate package folder structure inside DEST_DIR)
        # -o overwrite existing files without prompting
        unzip -j -o "$pkg" "*.sublime-syntax" -d "$DEST_DIR"
    fi
done

echo "Done! Syntaxes extracted to $DEST_DIR"