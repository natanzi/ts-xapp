# This is TS xApp version 1.0.0
import logging
import socket
import time
import os
from threading import Thread, Lock
from ricxappframe.xapp_frame import RMRXapp, rmr, Xapp
from menu import main_menu
from rmr_health_check import RMRHealthCheckXapp
from sdl_health_check import sdl_health_check
from alarm_handlers import handle_handover_failure, handle_data_retrieval_failure, handle_cell_congestion
from path.to.SubscriptionHandler import SubscriptionHandler  

# Initialize logging
logging.basicConfig(level=logging.INFO)

def main():
    rmr_health_check = None
    ts_xapp = None
    try:
        # Initialize RMR health check
        rmr_health_check = RMRHealthCheckXapp()
        if not rmr_health_check.rmr_health_check():
            logging.error("RMR health check failed. Exiting.")
            return

        # Perform SDL health check
        if not sdl_health_check():
            logging.error("SDL health check failed. Exiting.")
            return

        # Start the interactive menu
        main_menu()

        # Initialize and run the Traffic Steering xApp
        ts_xapp = TrafficSteering()
        ts_xapp.on_register()
        Thread(target=ts_xapp.run).start()

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        if ts_xapp and ts_xapp.server:
            ts_xapp.server.close()

if __name__ == "__main__":
    main()


