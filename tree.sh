#!/bin/bash
OUTPUT_DIR="folder_structure"
OUTPUT_FILE="folder_structure.txt"

# Append the tree structure to the text file
tree "$OUTPUT_DIR" >> "$OUTPUT_FILE"

echo "Folder structure appended to $OUTPUT_FILE"
