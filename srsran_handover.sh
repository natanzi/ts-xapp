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

######################### Install srsRAN #####################
sudo apt-get install build-essential cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev
sudo apt-get install libzmq3-dev
sudo add-apt-repository ppa:ettusresearch/uhd
sudo apt-get update
sudo apt-get install libuhd-dev libuhd4.1.0 uhd-host
git clone https://gitlab.eurecom.fr/oai/asn1c.git
cd asn1c
git checkout velichkov_s1ap_plus_option_group
autoreconf -iv
./configure
cd ..

# Define the destination directory where srsRAN is located
DEST_DIR="/home/ubnt/main-file-repo/oaic/srsRAN-e2"

# Define the URLs of the source files to be replaced
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
  else
    echo "Failed to download $url to $full_dest_path" >&2
    exit 1
  fi
done

echo "Files have been downloaded successfully."

# Navigate to the srsRAN build directory and build the project
cd "${DEST_DIR}"
if [ ! -d "build" ]; then
  mkdir build
fi
cd build
cmake ..
make -j$(nproc)
sudo make install
sudo ldconfig

# Export the environment variable for srsRAN
export SRS=`realpath .`
# Additional cmake configurations, assuming e2_bindings directory exists under ${SRS}
cmake ../ -DCMAKE_BUILD_TYPE=RelWithDebInfo \
          -DRIC_GENERATED_E2AP_BINDING_DIR=${SRS}/e2_bindings/E2AP-v01.01 \
          -DRIC_GENERATED_E2SM_KPM_BINDING_DIR=${SRS}/e2_bindings/E2SM-KPM \
          -DRIC_GENERATED_E2SM_GNB_NRT_BINDING_DIR=${SRS}/e2_bindings/E2SM-GNB-NRT
make -j$(nproc)
sudo make install
sudo ldconfig
sudo srsran_install_configs.sh service
