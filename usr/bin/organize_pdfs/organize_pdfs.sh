#!/bin/bash

set -x  # Enable debugging

# Prompt the user to enter the root folder path
echo "Enter the root folder path: "
read ROOT_FOLDER

# Convert to Unix-style path if needed (for WSL compatibility)
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    ROOT_FOLDER_UNIX=$(echo "$ROOT_FOLDER" | sed 's/\\/\//g' | sed 's/^C:/\/mnt\/c/')
    echo "Root folder (Unix-style): $ROOT_FOLDER_UNIX"
    python3 categorize_and_report.py "$ROOT_FOLDER_UNIX"
else
    echo "Root folder (original): $ROOT_FOLDER"
    python3 categorize_and_report.py "$ROOT_FOLDER"
fi

echo "PDF organization and reporting completed."
