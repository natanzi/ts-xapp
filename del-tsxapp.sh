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

# Function to cleanup port forwarding on script exit
cleanup() {
  echo "Stopping port forwarding..."
  if [ -n "$PORT_FORWARD_PID" ]; then
    kill $PORT_FORWARD_PID 2>/dev/null
    unset PORT_FORWARD_PID
    echo "Port forwarding stopped."
  else
    echo "No port forwarding process found."
  fi
}

# Function to free up a specified port
free_up_port() {
    local port=$1
    echo "Checking if port $port is in use..."
    local pid=$(sudo lsof -t -i:$port)
    if [ -n "$pid" ]; then
        local process_name=$(ps -p $pid -o comm=)
        echo "Port $port is in use by process $pid ($process_name). Attempting to free up..."
        
        # Optional: Ask for user confirmation
        read -p "Do you want to terminate process $pid ($process_name) using port $port? (y/n) " confirm
        if [ "$confirm" != "y" ]; then
            echo "User aborted the operation."
            exit 1
        fi

        # Send a SIGTERM signal first
        sudo kill $pid
        sleep 2

        # Check if the process is still running, and if so, force kill
        if ps -p $pid > /dev/null; then
            echo "Process did not terminate gracefully. Force killing..."
            sudo kill -9 $pid
        fi

        # Wait a moment and check if the port is freed up
        sleep 1
        if sudo lsof -t -i:$port > /dev/null; then
            echo "Failed to free up port $port"
            exit 1
        else
            echo "Port $port freed up successfully"
        fi
    else
        echo "Port $port is not in use."
    fi
}


# Set the trap function for script exit
trap cleanup EXIT

# Free up ports used by the xApp (if necessary)
free_up_port 5001
free_up_port 8086

# Check if InfluxDB is running in Kubernetes
if ! kubectl get pods -n $NAMESPACE | grep -q "$INFLUXDB_SERVICE"; then
    echo -e "${RED}InfluxDB is not running in Kubernetes. Please deploy InfluxDB and try again.${NC}"
    exit 1
fi
echo "InfluxDB is running."

# Port-forward InfluxDB
kubectl port-forward svc/$INFLUXDB_SERVICE 8086:8086 -n $NAMESPACE &
echo "InfluxDB port-forwarding setup complete."
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
    if [ "$resource" == "pods" ]; then
        kubectl delete $resource -n ricxapp -l app=ricxapp-ts-xapp --force --grace-period=0
    else
        kubectl delete $resource -n ricxapp -l app=ricxapp-ts-xapp
    fi
done
check_status "Failed to remove Kubernetes resources" "Kubernetes resources removed successfully"

echo -e "${GREEN}xApp undeployed and cleaned up successfully!${NC}"
