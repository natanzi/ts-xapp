#__init__.py
import json
import os
import sys
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler('init-ts-xapp.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../init/ts-xapp-config-file.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config
    except Exception as e:
        logging.error(f"Error loading json file from {config_path}. Reason = {str(e)}")
        sys.exit(1)

def set_environment_variables(config):
    try:
        os.environ["XAPP_NAME"] = config["xapp_name"]
        os.environ["VERSION"] = config["version"]
        os.environ["RMR_PORT"] = str(config["rmr"]["protPort"])
        # Add any other environment variables you need to set here
        return True
    except Exception as e:
        logging.error(f"Error setting environment variables. Reason = {str(e)}")
        return False

def start_ts_xapp():
    cmd = ["python3", "ts-xapp.py"]
    subprocess.run(cmd)

if __name__ == "__main__":
    config = load_config()
    
    if set_environment_variables(config):
        logging.info("Environment variables set successfully")
        start_ts_xapp()
    else:
        logging.error("Failed to set environment variables")
