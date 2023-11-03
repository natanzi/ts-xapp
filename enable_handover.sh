#!/bin/bash
# Ensure the script is run as root
#!/bin/bash

# Ensure the script is run as root
if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root" >&2
  exit 1
fi

# Check the current working directory
REQUIRED_DIR="/home/ubnt/main-file-repo/oaic"
if [ "$(pwd)" != "$REQUIRED_DIR" ]; then
  echo "This script must be run from $REQUIRED_DIR" >&2
  exit 1
fi

# Function to compare file checksums
compare_checksums() {
  local src_file=$1
  local dest_file=$2

  # Calculate MD5 checksums
  local src_checksum=$(md5sum "$src_file" | cut -d ' ' -f1)
  local dest_checksum=$(md5sum "$dest_file" | cut -d ' ' -f1)

  # Compare the checksums
  if [ "$src_checksum" == "$dest_checksum" ]; then
    echo "Checksums match for $src_file and $dest_file."
    return 0
  else
    echo "Checksums do not match for $src_file and $dest_file!" >&2
    return 1
  fi
}

# Define the local directory where downloaded files are placed
# Replace "/path/to/downloaded/files" with the actual path where the downloaded files are stored.
LOCAL_DIR="https://github.com/natanzi/srsRAN_4G_handover/"
DEST_DIR="/home/ubnt/main-file-repo/oaic/srsRAN-e2"

# Define an associative array with local and destination paths
declare -A files_to_copy=(
  ["$LOCAL_DIR/srsenb/src/main.cc"]="$DEST_DIR/srsenb/src/main.cc"
  ["$LOCAL_DIR/lib/include/srsran/common/handover_server.h"]="$DEST_DIR/lib/include/srsran/common/handover_server.h"
  ["$LOCAL_DIR/CMakeLists.txt"]="$DEST_DIR/CMakeLists.txt"
  ["$LOCAL_DIR/lib/src/common/handover_server.cpp"]="$DEST_DIR/lib/src/common/handover_server.cpp"
)

# Copy or create the files
for src in "${!files_to_copy[@]}"; do
  dest=${files_to_copy[$src]}
  dest_dir=$(dirname "$dest")

  # Create the destination directory if it doesn't exist
  mkdir -p "$dest_dir"

  # Check if the source file exists
  if [ -f "$src" ]; then
    # Copy the file and overwrite the destination
    cp -f "$src" "$dest" && echo "Copied $src to $dest"
    # Verify the copy by comparing checksums
    if ! compare_checksums "$src" "$dest"; then
      echo "Copy verification failed for $src to $dest" >&2
      exit 1
    fi
  else
    # If the source file does not exist, create an empty file at the destination
    touch "$dest" && echo "Created empty file at $dest"
  fi
done

echo "All files have been processed successfully."


