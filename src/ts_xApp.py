# This is Traffic Steering xApp version 1.0.0 by Milad Ntanzi
import socket
import time
import os
from threading import Thread, Lock
from ricxappframe.xapp_frame import RMRXapp, rmr, Xapp
from menu import main_menuclear
from rmr_health_check import RMRHealthCheckXapp
from sdl_health_check import sdl_health_check
from alarm_handlers import handle_handover_failure, handle_data_retrieval_failure, handle_cell_congestion
from path.to.SubscriptionHandler import SubscriptionHandler
from path.to.RMRManager import RMRManager
from config import Config  # Importing the Config class
from logger import AppLogger  # Importing the AppLogger class

def main():
    rmr_health_check = None
    ts_xapp = None
    rmr_manager = None  # RMR Manager instance
    subscription_handler = None  # Subscription handler instance
    config = None  # Configuration instance
    app_logger = None  # Logger instance

    try:
        # Load the configuration
        config = Config(xapp_name="ts-xApp", config_file="path/to/your/config.json")  # Replace with your actual xApp name and config file path

        # Initialize the logger
        app_logger = AppLogger(name="TS-xApp", verbose=2)  # Replace with your actual xApp name and desired verbosity level
        logger = app_logger.get_logger()

        # Initialize RMR health check
        rmr_health_check = RMRHealthCheckXapp(logger)  # Pass the logger to the RMRHealthCheckXapp
        if not rmr_health_check.rmr_health_check():
            logger.error("RMR health check failed. Exiting.")
            return

        # Perform SDL health check
        if not sdl_health_check():
            logger.error("SDL health check failed. Exiting.")
            return

        # Initialize RMR Manager
        rmr_manager = RMRManager(config, logger)  # Pass the config and logger to the RMRManager
        rmr_manager.start()  # Start RMR Manager

        # Initialize Subscription Handler
        subscription_handler = SubscriptionHandler(config, logger)  # Pass the config and logger to the SubscriptionHandler
        subscription_handler.subscribe()  # Subscribe to necessary events

        # Start the interactive menu
        main_menu()

        # Initialize and run the Traffic Steering xApp
        ts_xapp = TrafficSteering(config, logger)  # Pass the config and logger to the TrafficSteering xApp
        ts_xapp.on_register()
        Thread(target=ts_xapp.run).start()

    except Exception as e:
        if logger:
            logger.error(f"An error occurred: {e}")
        else:
            print(f"An error occurred: {e}")  # Fallback to standard print if the logger is not initialized

    finally:
        if ts_xapp and ts_xapp.server:
            ts_xapp.server.close()
        if rmr_manager:
            rmr_manager.stop()  # Ensure RMR Manager is stopped properly
        if subscription_handler:
            subscription_handler.unsubscribe()  # Clean up subscriptions

if __name__ == "__main__":
    main()
