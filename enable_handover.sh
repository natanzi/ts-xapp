#!/bin/bash

# The script should be placed in the root directory of the project.
REQUIRED_PWD="/path/to/your/project/root" # Replace with the actual required path.

# Target directory where files will be copied.
TARGET_DIR="/home/ubnt/main-file-repo/oaic/srsRAN-e2"

# Files to copy.
FILES_TO_COPY=(
  "srsRAN_4G_handover/srsenb/src/main.cc"
  "srsRAN_4G_handover/lib/include/srsran/common/handover_server.h"
  "srsRAN_4G_handover/CMakeLists.txt"
  "srsRAN_4G_handover/lib/src/common/handover_server.cpp"
)

# Check if the user is in the required pwd to run the script.
if [ "$(pwd)" != "$REQUIRED_PWD" ]; then
  echo "Error: This script must be run from $REQUIRED_PWD"
  exit 1
fi

# Copy the files.
for file in "${FILES_TO_COPY[@]}"; do
  if [ -f "$file" ]; then
    # Use the -f flag to force the copy and overwrite the destination files.
    cp -f "$file" "$TARGET_DIR/$(basename "$file")" || { 
      echo "Failed to copy $file to $TARGET_DIR"
      exit 1
    }
    echo "Copied $file to $TARGET_DIR"
  else
    echo "Error: File $file does not exist."
    exit 1
  fi
done

echo "All files have been copied successfully."
