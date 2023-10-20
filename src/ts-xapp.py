# This is Traffic Steering xApp version 1.0.0 by Milad Natanzi
import socket
import time
import os
from threading import Thread, Lock
from ricxappframe.xapp_frame import RMRXapp, rmr, Xapp
from config import Config  # Importing the Config class
from rmr_health_check import RMRHealthCheckXapp  # Importing the RMRHealthCheckXapp class

def main():
    config = None  # Configuration instance
    rmr_health_check = None  # RMR health check instance

    try:
        # Load the configuration
        config = Config(xapp_name="ts-lsxApp", config_file="/app/ts-xapp/init/ts-xapp-config-file.json") 

        # Initialize RMR health check
        rmr_health_check = RMRHealthCheckXapp()  # Removed logger from RMRHealthCheckXapp initialization
        if not rmr_health_check.rmr_health_check():
            print("RMR health check failed. Exiting.")  # Using standard print instead of logger
            return

    except Exception as e:
        print(f"An error occurred: {e}")  # Using standard print instead of logger

if __name__ == "__main__":
    main()
