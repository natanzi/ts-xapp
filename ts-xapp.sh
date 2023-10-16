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

git clone https://github.com/natanzi/ts-xapp

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
sleep 5
echo ">>> reloading nginx..."
sudo nginx -t || { echo 'nginx configuration test failed'; check_continue; }
cd ${oaic}
# Overwrite the file if it exists
sudo cp -f /home/ubnt/main-file-repo/oaic/ts-xapp/init/ts-xapp-config-file.json /var/www/xApp_config.local/config_files/ || { echo 'Failed to copy config file'; check_continue; }
[ -r "/var/www/xApp_config.local/config_files/ts-xapp-config-file.json" ] || { echo 'Config File not found or is not readable'; check_continue; }
ls -l /var/www/xApp_config.local/config_files/
pwd
sudo chmod 755 /var/www/xApp_config.local/config_files/ts-xapp-config-file.json || { echo 'Failed to change file permissions'; check_continue; }
sudo systemctl reload nginx || { echo 'Failed to reload nginx'; check_continue; }
echo ">>> getting machine IP..."
export MACHINE_IP=`hostname  -I | cut -f1 -d' '`
sleep 5
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
sleep 5
echo ">>> Checking if Docker image was successfully built..."

# Check if the Docker image was successfully created
IMAGE_EXISTS=$(sudo docker image ls | grep "xApp-registry.local:5008/ts-xapp" | grep "1.0.0")

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
  sudo docker images --filter=reference='xApp-registry.local:5008/ts-xapp:1.0.0'
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
echo ">>> xApp Onboarder Deployment"
echo ">>> Before Deploying the xApp, it is essential to have the 5G Network Up and Running. Otherwise the subscription procedure will not be successful."

# Retrieve service IPs and check the status of each command
export KONG_PROXY=$(sudo kubectl get svc -n ricplt -l app.kubernetes.io/name=kong -o jsonpath='{.items[0].spec.clusterIP}')
check_status "Failed to retrieve KONG_PROXY"
sleep 5
export APPMGR_HTTP=$(sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-appmgr-http -o jsonpath='{.items[0].spec.clusterIP}')
check_status "Failed to retrieve APPMGR_HTTP"
sleep 5
export ONBOARDER_HTTP=$(sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-xapp-onboarder-http -o jsonpath='{.items[0].spec.clusterIP}')
check_status "Failed to retrieve ONBOARDER_HTTP"
############################################################################
# Display the retrieved variables
RED='\033[0;31m' # Red color
NC='\033[0m' # No Color

# This line will be displayed in red
echo -e "${RED}>>> Get Variables.....First, we need to get some variables of RIC Platform ready. The following variables represent the IP addresses of the services running on the RIC Platform.${NC}"

# These lines display the variables with their values in red
export MACHINE_IP=`hostname  -I | cut -f1 -d' '`
echo -e "KONG_PROXY = ${RED}$KONG_PROXY${NC}"
echo -e "APPMGR_HTTP = ${RED}$APPMGR_HTTP${NC}"
echo -e "ONBOARDER_HTTP = ${RED}$ONBOARDER_HTTP${NC}"
echo -e "Machine IP: ${RED}$MACHINE_IP${NC}"
############################################################################
# Check for helm charts
echo ">>> getting charts ... Check for helm charts"
curl --location --request GET "http://$KONG_PROXY:32080/onboard/api/v1/charts"
check_status "Failed to get charts"
sleep 5
############################################################################
# Prepare the JSON file for xApp onboarding
echo '{"config-file.json_url":"http://'$MACHINE_IP':5010/config_files/ts-xapp-config-file.json"}' > ts-xapp-onboard.url
check_status "Failed to create ts-xapp-onboard.url"

echo ">>> ts-xapp-onboard.url"
cat ts-xapp-onboard.url
sleep 5

# Attempt to onboard the xApp
echo ">>> curl POST... Now we are ready to deploy the xApp"
curl -L -X POST "http://$KONG_PROXY:32080/onboard/api/v1/onboard/download" --header 'Content-Type: application/json' --data-binary "@ts-xapp-onboard.url"
check_status "Failed to post onboard download"

# Check the onboarded charts
echo ">>> curl GET..."
curl -L -X GET "http://$KONG_PROXY:32080/onboard/api/v1/charts"
check_status "Failed to get charts after onboarding"
sleep 5

# Attempt to post the xApp
echo ">>> curl POST..."
curl -L -X POST "http://$KONG_PROXY:32080/appmgr/ric/v1/xapps" --header 'Content-Type: application/json' --data-raw '{"xappName": "ts-xapp"}'
check_status "Failed to post xApp"

echo 'Successful: ts-xapp up and running'
sleep 5
# Verifying xApp Deployment
echo 'We should see a ricxapp-ts-xapp pod in the ricxapp namespace. This command lists all the pods in all namespaces.'
echo 'Verifying xApp Deployment...'
sudo kubectl get pods -A
POD_STATUS=$(sudo kubectl get pods -n ricxapp | grep ricxapp-ts-xapp)

if [ -z "$POD_STATUS" ]; then
    echo "No ricxapp-ts-xapp pods found in the ricxapp namespace."
else
    echo "$POD_STATUS"
fi

# Check if the user wants to see the xApp logs
read -p "Do you see the ricxapp-ts-xapp in the list and want to check its logs? (y/n): " choice
case "$choice" in 
  y|Y )
    echo 'Checking xApp logs...'
    sudo kubectl logs -f -n ricxapp -l app=ricxapp-ts-xapp
    ;;
  n|N )
    echo "Skipping xApp logs..."
    ;;
  * ) 
    echo "Invalid input"
    ;;
esac
# To ensure successful deployment, you should see the expected logs without any error messages, and the status of the pods should be 'Running'.
