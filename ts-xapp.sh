cat << 'EOF'
################################################################################
#          Welcome to OAIC Traffic Steering xApp Fast Installation             #
#                                                                              #
#   This script installs Nginx and configures the necessary files for running  #
#   the Traffic Steering (TS) xApp on OAIC Testbed.                                            #
#                                                                              #
#   The Traffic Steering (TS) xApp is a specialized tool designed for the      #
#   OAIC O-RAN testbed. Its primary purpose is to efficiently manage and       #
#   optimize traffic flow within cellular networks. By utilizing real-time     #
#   metrics and adhering to dynamic policies, this xApp ensures optimal        #
#   network performance by making informed decisions about user equipment      #
#   (UE) handovers between cells. This xApp can be onboarded through the       #
#   xApp Onboarder.                                                            #
#                                                                              #
#   Licensed under the Apache License, Version 2.0 (the "License");            #
#   you may not use this file except in compliance with the License.           #
#   You may obtain a copy of the License at:                                   #
#       http://www.apache.org/licenses/LICENSE-2.0                             #
#                                                                              #
#   Unless required by applicable law or agreed to in writing, software        #
#   distributed under the License is distributed on an "AS IS" BASIS,          #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
#   See the License for the specific language governing permissions and        #
#   limitations under the License.                                             #
################################################################################
EOF
################################################################################
create_docker_network() {
    local network_name="$1"
    
    # Check if the Docker network already exists
    DOCKER_NETWORK_EXISTS=$(docker network ls | grep "$network_name")
    
    if [ -z "$DOCKER_NETWORK_EXISTS" ]; then
        echo "Creating Docker network '$network_name'..."
        docker network create "$network_name"
        echo "Docker network '$network_name' created successfully."
    else
        echo "Docker network '$network_name' already exists. Proceeding to the next steps..."
    fi
}
#################################################################################
create_docker_network "my_network"
#################################################################################
# Function to check if the script encounters any issues and prompts the user to continue or exit
function check_continue() {
    read -p "An issue occurred. Do you want to continue? (y/n): " choice
    case "$choice" in 
      y|Y ) echo "Continuing...";;
      n|N ) echo "Exiting..."; exit 1;;
      * ) echo "Invalid input"; check_continue;;
    esac
}

# Check if the script is being run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Check if the current directory is /home/ubnt/oaic/ts-xapp
if [ "$(pwd)" != "/home/ubnt/main-file-repo/oaic/ts-xapp" ]; then
    echo "This script must be run from the /home/ubnt/oaic directory"
    exit 1
fi

echo "Installing iperf3..."
sudo apt install iperf3 || { echo 'iperf3 installation failed'; check_continue; }
echo "iperf3 installation completed."

echo "Installing vim..."
sudo apt install vim || { echo 'vim installation failed'; check_continue; }
echo "vim installation completed."
apt install python3-pip


oaic=`pwd`
echo "Installing nginx..."
sudo apt-get install nginx || { echo 'nginx installation failed'; check_continue; }
echo "nginx installation completed."  # Corrected here (added closing quotation mark)
sleep 5
sudo systemctl start nginx.service || { echo 'Failed to start nginx'; check_continue; }
# New command to check the status of nginx
sudo systemctl status nginx --no-pager || { echo 'nginx service is not running'; check_continue; }
cd /etc/nginx/sites-enabled
if [ -e "default" ]; then
    sudo unlink default || { echo 'Failed to unlink default'; check_continue; }
else
    echo "'default' file does not exist, skipping unlink."
fi
cd ../
cd ../../var/www
# Check if directory exists, if not create it
if [ ! -d "xApp_config.local" ]; then
  sudo mkdir xApp_config.local || { echo 'Failed to create directory xApp_config.local'; check_continue; }
else
  echo "Directory xApp_config.local already exists."
fi
cd xApp_config.local/
# Check if directory exists, if not create it
if [ ! -d "config_files" ]; then
  sudo mkdir config_files || { echo 'Failed to create directory config_files'; check_continue; }
else
  echo "Directory config_files already exists."
fi
cd ../../../etc/nginx/conf.d
# Overwrite the file if it exists
sudo sh -c "echo 'server {
listen 5010 default_server;
server_name xApp_config.local;
location /config_files/ {
root /var/www/xApp_config.local/;
}
}' >xApp_config.local.conf"

echo ">>> reloading nginx..."
sleep 3

sudo nginx -t || { echo 'nginx configuration test failed'; check_continue; }
cd ${oaic}
# Overwrite the file if it exists
sudo cp -f /home/ubnt/main-file-repo/oaic/ts-xapp/init/ts-xapp-config-file.json /var/www/xApp_config.local/config_files/ || { echo 'Failed to copy config file'; check_continue; }
[ -r "/var/www/xApp_config.local/config_files/ts-xapp-config-file.json" ] || { echo 'Config File not found or is not readable'; check_continue; }
ls -l /var/www/xApp_config.local/config_files/
pwd
#sudo chmod 755 /var/www/xApp_config.local/config_files/ts-xapp-config-file.json || { echo 'Failed to change file permissions'; check_continue; }
sudo systemctl reload nginx || { echo 'Failed to reload nginx'; check_continue; }
echo ">>> getting machine IP..."
export MACHINE_IP=`hostname  -I | cut -f1 -d' '`
sleep 3
echo "Machine IP: $MACHINE_IP"
echo ">>> checking for config-file"
curl http://${MACHINE_IP}:5010/config_files/ts-xapp-config-file.json || { echo 'Failed to fetch config-file'; check_continue; }
echo ">>> building docker image...."
cd ${oaic}/ts-xapp
echo ">>> checking directory"
ls
echo ">>> Creating ts-xapp Docker image"
echo ">>> Now, we create a docker image of the ts-xApp using the given docker file."
sudo docker build . -t xApp-registry.local:5008/ts-xapp:1.0.0 || { echo 'docker build failed'; check_continue; }

# Check if the Docker image was successfully created
IMAGE_EXISTS=$(sudo docker image ls | grep "xApp-registry.local:5008/ts-xapp" | grep "1.0.0")

# Check if the image exists
if [ -n "$IMAGE_EXISTS" ]; then
    # Print the result in a rectangle with '#'
    echo "################################################################################################################################"
    echo "#                                                                                                                              #"
    echo "#    Docker Image Found:                                                                                                       #"
    echo "#    $IMAGE_EXISTS                                                                                                             #"
    echo "#                                                                                                                              #"
    echo "################################################################################################################################"
else
    echo "################################################################################################################################"
    echo "#                                                                                                                              #"
    echo "#    No Docker Image Found for ts-xapp !                                                                                       #"
    echo "#                                                                                                                              #"
    echo "################################################################################################################################"
fi

if [ -z "$IMAGE_EXISTS" ]; then
  echo "Docker image build failed. Do you want to exit the script? (y/n): "
  read response
  if [[ "$response" == "y" || "$response" == "Y" ]]; then
    echo "Exiting script."
    exit 1
  else
    echo "Continuing script."
    # Continue with other operations or retry logic
  fi
else
  echo "Docker image built successfully. Here are the details:"
  echo "################################################################################################################################"
  echo "#                                                                                                                              #"
  # Execute the command and display its output
  sudo docker images --filter=reference='xApp-registry.local:5008/ts-xapp:1.0.0'
  echo "#                                                                                                                              #"
  echo "################################################################################################################################"
   
fi

echo "Pausing for 20 seconds to allow system processes to stabilize before continuing..."
sleep 20

###############################################################################
# Function to check the status of the last command executed
check_status() {
    if [ $? -ne 0 ]; then
        echo "Error: $1" >&2
        exit 1
    fi
}
##############################################################################
# Set the namespace and service name
NAMESPACE="ricxapp"
SERVICE_NAME="ts-xapp-service"

# Check if the service already exists
if kubectl get svc $SERVICE_NAME -n $NAMESPACE > /dev/null 2>&1; then
    echo "$SERVICE_NAME already exists in namespace $NAMESPACE."
else
    # Apply the configuration
    kubectl apply -f ts-xapp-service.yaml
    
    # Check if the service creation was successful
    if kubectl get svc $SERVICE_NAME -n $NAMESPACE > /dev/null 2>&1; then
        echo "$SERVICE_NAME successfully created in namespace $NAMESPACE."
    else
        echo "Failed to create $SERVICE_NAME in namespace $NAMESPACE."
        exit 1
    fi
fi

# Describe the service
kubectl describe svc $SERVICE_NAME -n $NAMESPACE
##############################################################################
echo ">>> Enter to xApp onboarder deployment process..."
echo ">>> Before Deploying the xApp, it is essential to make sure the 5G Network Up and Running. Otherwise the subscription procedure will not be successful."

# Retrieve service IPs and check the status of each command
export KONG_PROXY=$(sudo kubectl get svc -n ricplt -l app.kubernetes.io/name=kong -o jsonpath='{.items[0].spec.clusterIP}')
check_status "Failed to retrieve KONG_PROXY"

export APPMGR_HTTP=$(sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-appmgr-http -o jsonpath='{.items[0].spec.clusterIP}')
check_status "Failed to retrieve APPMGR_HTTP"

export ONBOARDER_HTTP=$(sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-xapp-onboarder-http -o jsonpath='{.items[0].spec.clusterIP}')
check_status "Failed to retrieve ONBOARDER_HTTP"
############################################################################
# Display the retrieved variables
RED='\033[0;31m' # Red color
NC='\033[0m' # No Color
GREEN='\033[0;32m' # Green color

# This line will be displayed in red
echo -e ">>> Get Variables.....First, we need to get some variables of RIC Platform ready. The following variables represent the IP addresses of the services running on the RIC Platform."

# These lines display the variables with their values in red
export MACHINE_IP=$(hostname  -I | cut -f1 -d' ')
echo -e "KONG_PROXY = ${GREEN}$KONG_PROXY${NC}"
echo -e "APPMGR_HTTP = ${GREEN}$APPMGR_HTTP${NC}"
echo -e "ONBOARDER_HTTP = ${GREEN}$ONBOARDER_HTTP${NC}"
echo -e "Machine IP: ${GREEN}$MACHINE_IP${NC}"
############################################################################
# Check for helm charts
echo ">>> getting charts ... Check for helm charts"
curl -v --location --request GET "http://$KONG_PROXY:32080/onboard/api/v1/charts"
check_status "Failed to get charts"

############################################################################
# Prepare the JSON file for xApp onboarding
echo '{"config-file.json_url":"http://'$MACHINE_IP':5010/config_files/ts-xapp-config-file.json"}' > ts-xapp-onboard.url
check_status "Failed to create ts-xapp-onboard.url"

echo ">>> ts-xapp-onboard.url"
cat ts-xapp-onboard.url

# Attempt to onboard the xApp
echo ">>> curl POST... Now we are ready to deploy the xApp"
curl -v -L -X POST "http://$KONG_PROXY:32080/onboard/api/v1/onboard/download" --header 'Content-Type: application/json' --data-binary "@ts-xapp-onboard.url"
check_status "Failed to post onboard download"

# Check the onboarded charts
echo ">>> curl GET..."
curl -v -L -X GET "http://$KONG_PROXY:32080/onboard/api/v1/charts"
check_status "Failed to get charts after onboarding"


# Colors for output
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check the status of the previous command
check_status() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}$1${NC}"
        exit 1
    fi
}

# Colors for output
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check the status of the previous command
check_status() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}$1${NC}"
        exit 1
    fi
}

# Attempt to post the xApp
echo ">>> curl POST..."
curl -v -L -X POST "http://$KONG_PROXY:32080/appmgr/ric/v1/xapps" --header 'Content-Type: application/json' --data-raw '{"xappName": "ts-xapp"}'
check_status "Failed to post xApp"

# Verifying xApp Deployment
echo 'Verifying xApp Deployment...'
sudo kubectl get pods -A
echo "################################################################################################################################"
echo "#                                                                                                                              #"
echo "# Verifying xApp Deployment...                                                                                                 #"

# Capture the output of the command you want to run
POD_STATUS=$(sudo kubectl get pods -A | grep ricxapp-ts-xapp)

# Check if the variable doesn't contain anything
if [ -z "$POD_STATUS" ]; then
    echo "# No ricxapp-ts-xapp pods found in the ricxapp namespace.                                                                     #"
else
    # If the variable contains output, print it
    echo "# $POD_STATUS                                                                                                                #"
fi

echo "#                                                                                                                              #"
echo "################################################################################################################################"
echo "################################################################################################################################"
echo "######################################### Setting up Grafana... ################################################################"
echo "################################################################################################################################"

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker and try again.${NC}"
    exit 1
fi

DOCKER_RUNNING=$(systemctl is-active docker)
if [ "$DOCKER_RUNNING" != "active" ]; then
    echo -e "${RED}Docker service is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Pull and run Grafana container
GRAFANA_CONTAINER_EXISTS=$(docker ps -a | grep "grafana")
if [ -z "$GRAFANA_CONTAINER_EXISTS" ]; then
    docker pull grafana/grafana
    docker run -d --name=grafana --network=my_network -p 3000:3000 grafana/grafana
else
    echo "Grafana container already exists. Starting it if it's not running..."
    docker start grafana
fi

# Check if Grafana container is up and running
GRAFANA_STATUS=$(docker ps | grep "grafana/grafana")
if [ -z "$GRAFANA_STATUS" ]; then
    echo -e "${RED}Error: Grafana container not running.${NC}"
    exit 1
else
    echo "Grafana is up and running at http://localhost:3000"
fi

echo "################################################################################################################################"
echo "# Connecting ts-xapp to Docker Network and Running with Exposed Ports"
echo "################################################################################################################################"

# Check if ts-xapp container is already running
TS_XAPP_RUNNING=$(docker ps | grep "ts-xapp")
if [ -n "$TS_XAPP_RUNNING" ]; then
    echo "ts-xapp container is already running. Checking if it is connected to 'my_network'..."
    
    if ! docker network inspect my_network | grep -q "ts-xapp"; then
        # Connect ts-xapp to Docker network (if not already connected)
        echo "Connecting ts-xapp container to 'my_network' Docker network..."
        docker network connect my_network ts-xapp
        echo "ts-xapp container is now connected to 'my_network' Docker network."
        sleep 5  # Wait for Docker to update its internal state
    fi
else
    # Run ts-xapp container with the exposed InfluxDB port
    echo "Running ts-xapp container with exposed ports for InfluxDB and connecting it to 'my_network'..."
    docker run -d --name ts-xapp -p 8086:8086 --network my_network xApp-registry.local:5008/ts-xapp:1.0.0 && echo "Container started successfully" || echo "Failed to start container"
    
    # Wait for the ts-xapp container to be in the running state
    echo "Waiting for ts-xapp container to be in the running state..."
    for i in {1..30}; do
        if docker ps | grep -q "ts-xapp"; then
            echo "ts-xapp container is now running."
            break
        fi
        sleep 1
    done
    
    if ! docker ps | grep -q "ts-xapp"; then
        echo "Error: ts-xapp container did not start successfully."
        exit 1
    fi
fi

# Additional check to ensure ts-xapp is connected to my_network
for i in {1..20}; do
    if docker network inspect my_network | grep -q "ts-xapp"; then
        echo "ts-xapp container is confirmed to be connected to 'my_network'."
        exit 0
    else
        echo "Waiting for ts-xapp container to connect to 'my_network'..."
        sleep 2
    fi
done

echo "Error: ts-xapp container is not connected to 'my_network'."
exit 1

echo "################################################################################################################################"



# List all running containers along with their network connections
echo "Listing all running containers with their network connections:"
docker ps --format 'table {{.Names}}\t{{.Networks}}'

# Inspect the specific Docker network
echo "Inspecting 'my_network' Docker network:"
docker network inspect my_network
echo "################################################################################################################################"


# Function to cleanup port forwarding on script exit
function cleanup {
  echo "Stopping port forwarding..."
  if [ -n "$PORT_FORWARD_PID" ]; then
    kill $PORT_FORWARD_PID
  fi
}

# Set the trap function for script exit
trap cleanup EXIT

# Check if the user wants to see the xApp logs
while true; do
    read -p "Do you see the ricxapp-ts-xapp in the list and want to check its logs? (y/n): " choice
    case "$choice" in 
      y|Y )
        echo 'Checking xApp logs...'
        # Retrieve the Pod Name
        POD_NAME=$(kubectl get pods -n ricxapp -l app=ricxapp-ts-xapp -o jsonpath='{.items[0].metadata.name}')
        
        # Start port-forward in the background
        kubectl port-forward pod/$POD_NAME 5001:5001 -n ricxapp &
        PORT_FORWARD_PID=$!
        echo "Port forwarding is now running in the background. PID: $PORT_FORWARD_PID"

        # Check xApp logs
        if ! sudo kubectl logs -f -n ricxapp -l app=ricxapp-ts-xapp; then
            echo "Error: Failed to retrieve logs. Make sure your cluster is reachable and the ricxapp-ts-xapp is deployed correctly."
        fi
        
        # Kill the port-forwarding process after checking the logs
        kill $PORT_FORWARD_PID
        unset PORT_FORWARD_PID

        break ;;
      n|N )
        echo "Skipping xApp logs..."
        break ;;
      * ) 
        echo "Invalid input, please enter 'y' for yes or 'n' for no."
    esac
done
