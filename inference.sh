#!/bin/bash
if [[ "$1" == "--help" ]]; then
    echo "Usage: ./script.sh <path_to_dir>"
    echo "Description: This script run model on all the .mp4 files in the specified directory."
    echo "Options:"
    echo "  --help       Display this help message."
    exit 0
fi

path_to_dir="$1"

for file in "$path_to_dir"/*.mp4; do
        python main.py -v $file
done