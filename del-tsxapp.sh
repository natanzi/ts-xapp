#!/bin/bash

# Set colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to check the status of the previous command
check_status() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}$1${NC}"
        exit 1
    else
        echo -e "${GREEN}$2${NC}"
    fi
}

# Retrieve the IP addresses of necessary services
export APPMGR_HTTP=$(sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-appmgr-http -o jsonpath='{.items[0].spec.clusterIP}')
check_status "Failed to retrieve APPMGR_HTTP IP" "APPMGR_HTTP IP retrieved successfully: $APPMGR_HTTP"

export ONBOARDER_HTTP=$(sudo kubectl get svc -n ricplt --field-selector metadata.name=service-ricplt-xapp-onboarder-http -o jsonpath='{.items[0].spec.clusterIP}')
check_status "Failed to retrieve ONBOARDER_HTTP IP" "ONBOARDER_HTTP IP retrieved successfully: $ONBOARDER_HTTP"

# Undeploy the xApp
echo "Deleting xApp from App Manager..."
curl -L -X DELETE http://${APPMGR_HTTP}:8080/ric/v1/xapps/ts-xapp
check_status "Failed to delete xApp from App Manager" "xApp deleted from App Manager successfully"

# Remove xApp descriptors from Chart Museum
echo "Removing xApp descriptors from Chart Museum..."
curl -L -X DELETE "http://${ONBOARDER_HTTP}:8080/api/charts/ts-xapp/1.0.0"
check_status "Failed to remove xApp descriptors from Chart Museum" "xApp descriptors removed from Chart Museum successfully"

# Delete Docker image
echo "Deleting Docker image..."
sudo docker rmi -f xApp-registry.local:5008/ts-xapp:1.0.0
check_status "Failed to delete Docker image" "Docker image deleted successfully"

# Remove Kubernetes resources associated with the xApp
echo "Removing Kubernetes resources associated with the xApp..."
for resource in pods services deployments; do
    kubectl delete $resource -n ricxapp -l app=ricxapp-ts-xapp
done
check_status "Failed to remove Kubernetes resources" "Kubernetes resources removed successfully"

echo -e "${GREEN}xApp undeployed and cleaned up successfully!${NC}"
