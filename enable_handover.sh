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

# Define the destination directory
DEST_DIR="/home/ubnt/main-file-repo/oaic/srsRAN-e2"

# Define the URLs of the source files
declare -A files_to_download=(
  ["srsenb/src/main.cc"]="https://raw.githubusercontent.com/natanzi/srsRAN_4G_handover/master/srsenb/src/main.cc"
  ["lib/include/srsran/common/handover_server.h"]="https://raw.githubusercontent.com/natanzi/srsRAN_4G_handover/master/lib/include/srsran/common/handover_server.h"
  ["CMakeLists.txt"]="https://raw.githubusercontent.com/natanzi/srsRAN_4G_handover/master/CMakeLists.txt"
  ["lib/src/common/handover_server.cpp"]="https://raw.githubusercontent.com/natanzi/srsRAN_4G_handover/master/lib/src/common/handover_server.cpp"
)

# Download and copy files
for dest_path in "${!files_to_download[@]}"; do
  url=${files_to_download[$dest_path]}
  full_dest_path="${DEST_DIR}/${dest_path}"

  # Create destination directory if it doesn't exist
  mkdir -p "$(dirname "$full_dest_path")"

  # Download the file using wget or curl
  if wget -q -O "$full_dest_path" "$url" || curl -s -o "$full_dest_path" "$url"; then
    echo "Downloaded $url to $full_dest_path"
    # Verify the download by comparing checksums with the online file
    if ! compare_checksums <(curl -s "$url") "$full_dest_path"; then
      echo "Download verification failed for $url to $full_dest_path" >&2
      exit 1
    fi
  else
    echo "Failed to download $url to $full_dest_path" >&2
    exit 1
  fi
done

echo "All files have been downloaded and verified successfully."
