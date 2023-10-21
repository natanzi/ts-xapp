# This is Traffic Steering xApp version 1.0.0 by Milad Natanzi

import os
import logging
from flask import Flask, jsonify
from ricxappframe.xapp_frame import RMRXapp, rmr, Xapp
import subprocess

# Set up logging
logging.basicConfig(filename='ts-xapp.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

app = Flask(__name__)


@app.route('/rmr_health_check', methods=['POST'])
def run_rmr_health_check():
    try:
        rmr_health_check()
        logging.info("RMR Health Check executed")
        return jsonify(message="RMR Health Check executed")
    except Exception as e:
        logging.error(f"Error executing RMR Health Check: {str(e)}")
        return jsonify(message=f"Error: {str(e)}"), 500


@app.route('/sdl_health_check', methods=['POST'])
def run_sdl_health_check():
    try:
        sdl_health_check()
        logging.info("SDL Health Check executed")
        return jsonify(message="SDL Health Check executed")
    except Exception as e:
        logging.error(f"Error executing SDL Health Check: {str(e)}")
        return jsonify(message=f"Error: {str(e)}"), 500


@app.route('/traffic_steering', methods=['POST'])
def run_traffic_steering():
    try:
        Traffic_Steering()
        logging.info("Traffic Steering function executed")
        return jsonify(message="Traffic Steering function executed")
    except Exception as e:
        logging.error(f"Error executing Traffic Steering: {str(e)}")
        return jsonify(message=f"Error: {str(e)}"), 500


if __name__ == "__main__":
    # Start dashboard.py as a separate process
    subprocess.Popen(["python3", "/path/to/dashboard.py"])
    
    logging.info("ts-xApp starting...")
    app.run(host='0.0.0.0', port=8080)  # You can adjust the port as needed

