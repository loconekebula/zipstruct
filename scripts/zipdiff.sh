#!/usr/bin/env bash

# Default values
ORIGINAL_DEFAULT="/home/kebula/Desktop/projects/ZipHashC2PA/data/inp/original_0.xlsx"
MODIFIED_DEFAULT="/home/kebula/Desktop/projects/ZipHashC2PA/data/tmp/appended.zip"

# Accept arguments or use defaults
original="${1:-$ORIGINAL_DEFAULT}"
modified="${2:-$MODIFIED_DEFAULT}"

# Check if files exists
if [[ ! -f "$original" ]]; then
    echo "File 1 does not exist ($original)."
    exit 1
fi
if [[ ! -f "$modified" ]]; then
    echo "File 2 does not exist ($modified)"
    exit 1
fi

# Actual zipdiff
diff <(zipinfo -v $original) <(zipinfo -v $modified)
