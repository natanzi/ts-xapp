#!/bin/bash

# Function to display a formatted message with a counter
print_progress() {
  local message="$1"
  local counter="$2"
  printf "\r\e[2K[\e[1;32m%s\e[0m] %s" "${counter}" "${message}"
}

# Function to prompt user to continue or exit on error
prompt_continue_or_exit() {
  echo -e "\n\nError occurred during installation."
  read -p "Do you want to continue? (Y/N): " choice
  if [[ "$choice" =~ ^[Yy]$ ]]; then
    return 0
  else
    echo "Exiting the script."
    exit 1
  fi
}

# Update package list
sudo apt update

# Counter for tracking progress
counter=0


# Clone and setup the git repository
echo -e "\n\nPart 2: Cloning the git repository..."
git clone https://github.com/openaicellular/oaic.git
cd oaic
git submodule update --init --recursive --remote
cd RIC-Deployment/tools/k8s/bin
./gen-cloud-init.sh
sudo ./k8s-1node-cloud-init-k_1_16-h_2_17-d_cur.sh
sudo kubectl get ns ricinfra
sudo kubectl create ns ricinfra
sudo helm install stable/nfs-server-provisioner --namespace ricinfra --name nfs-release-1
sudo kubectl patch storageclass nfs -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
sudo apt-get install nfs-common

sudo docker run -d -p 5001:5000 --restart=always --name ric registry:2
cd ../../../..
cd ric-plt-e2

cd RIC-E2-TERMINATION
sudo docker build -f Dockerfile -t localhost:5001/ric-plt-e2:5.5.0 .
sudo docker push localhost:5001/ric-plt-e2:5.5.0
cd ../../

# Part 3: Installing packages using Docker and other steps

#cd ../../../..
cd RIC-Deployment/bin


sudo ./deploy-ric-platform -f ../RECIPE_EXAMPLE/PLATFORM/example_recipe_oran_e_release_modified_e2.yaml

# Done message
echo -e "\n\nOAIC-Project setup completed successfully!\n"
