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

# Check if the current directory is /home/ubnt/oaic
if [ "$(pwd)" != "/home/ubnt/oaic" ]; then
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
sudo nginx -t || { echo 'nginx configuration test failed'; check_continue; }
cd ${oaic}
# Overwrite the file if it exists
sudo cp -f /home/ubnt/oaic/ts-xapp/init/ts-xapp-config-file.json /var/www/xApp_config.local/config_files/ || { echo 'Failed to copy config file'; check_continue; }
[ -r "/var/www/xApp_config.local/config_files/ts-xapp-config-file.json" ] || { echo 'Config File not found or is not readable'; check_continue; }
ls -l /var/www/xApp_config.local/config_files/
pwd
sudo chmod 755 /var/www/xApp_config.local/config_files/ts-xapp-config-file.json || { echo 'Failed to change file permissions'; check_continue; }
sudo systemctl reload nginx || { echo 'Failed to reload nginx'; check_continue; }
echo ">>> getting machine IP..."
export MACHINE_IP=`hostname  -I | cut -f1 -d' '`

echo ">>> checking for config-file"
curl http://${MACHINE_IP}:5010/config_files/ts-xapp-config-file.json || { echo 'Failed to fetch config-file'; check_continue; }
echo ">>> building docker image...."
cd ${oaic}/ts-xapp
echo ">>> checking directory"
ls
echo ">>> Creating ts-xapp Docker image"
echo ">>> Now, we create a docker image of the ts-xApp using the given docker file."
sudo docker build . -t xApp-registry.local:5008/ts-xapp:1.0.0 || { echo 'docker build failed'; check_continue; }

sleep 20

echo ">>> xApp Onboarder Deployment"
echo ">>> Before Deploying the xApp, it is essential to have the 5G Network Up and Running. Otherwise the subscription procedure will not be successful."
export KONG_PROXY=`sudo kubectl get svc -n ricplt -l app.kubernetes.io/name=kong -o jsonpath='{.items[0].spec.clusterIP}'`
export APPMGR_HTTP=`sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-appmgr-http -o jsonpath='{.items[0].spec.clusterIP}'`
export ONBOARDER_HTTP=`sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-xapp-onboarder-http -o jsonpath='{.items[0].spec.clusterIP}'`

echo ">>> Get Variables.....First, we need to get some variables of RIC Platform ready. The following variables represent the IP addresses of the services running on the RIC Platform."
echo "KONG_PROXY = $KONG_PROXY"
echo "APPMGR_HTTP = $APPMGR_HTTP"
echo "ONBOARDER_HTTP = $ONBOARDER_HTTP"

echo ">>> getting charts ... Check for helm charts"
echo ">>> Get helm charts and check if the current xApp is one of them. If there is no helm chart, then we are good to go. Otherwise, we have to use the existing chart or delete it and then proceed forward."
curl --location --request GET "http://$KONG_PROXY:32080/onboard/api/v1/charts" || { echo 'Failed to get charts'; check_continue; }
ls
echo '{"config-file.json_url":"http://'$MACHINE_IP':5010/config_files/ts-xapp-config-file.json"}' > ts-xapp-onboard.url

echo ">>> ts-xapp-onboard.url"
cat ts-xapp-onboard.url
echo ">>> curl POST... Now we are ready to deploy the xApp"
curl -L -X POST "http://$KONG_PROXY:32080/onboard/api/v1/onboard/download" --header 'Content-Type: application/json' --data-binary "@ts-xapp-onboard.url" || { echo 'Failed to post onboard download'; check_continue; }

echo ">>> curl GET..."
curl -L -X GET "http://$KONG_PROXY:32080/onboard/api/v1/charts" || { echo 'Failed to get charts'; check_continue; }
echo ">>> curl POST..."
curl -L -X POST "http://$KONG_PROXY:32080/appmgr/ric/v1/xapps" --header 'Content-Type: application/json' --data-raw '{"xappName": "ts-xapp"}' || { echo 'Failed to post xApp'; check_continue; }

echo 'Successful: ts-xapp up and running'

# Verifying xApp Deployment
echo 'We should see a ricxapp-ts-xapp pod in the ricxapp namespace. This command lists all the pods in all namespaces.'
echo 'Verifying xApp Deployment...'
sudo kubectl get pods -n ricxapp | grep ricxapp-ts-xapp

# Check if the user wants to see the xApp logs
read -p "Do you see the ricxapp-ts-xapp in the list and want to check its logs? (y/n): " choice
case "$choice" in 
  y|Y )
    echo 'Checking xApp logs...'
    # This command will show us the logs of the pod with the label app=ricxapp-ts-xapp in the ricxapp namespace.
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
