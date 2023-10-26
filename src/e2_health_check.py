#e2_health_check.py
import json
import logging
import signal
import time
from ricxappframe.xapp_frame import RICMessage, RICRegion, RICService, RICSubscription
from ricxappframe.xapp_frame import RICXapp, RICXappException

class E2HealthCheck(RICXapp):
    def __init__(self):
        super().__init__("E2HealthCheck")
        self.subscription_id = None
        self.subscribed = False

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)  # Default handler for SIGINT

        # Initialize the E2 interface
        self.e2_init()
        self.e2_register_callback(self.e2_message_handler)

        # Register the RIC subscription
        self.subscription_id = self.register_subscription(RICSubscription.RIC_SUB_REQ_SUBDEL, None, self.subscription_callback)
        logging.info("Registered subscription with subscription ID: %s", self.subscription_id)

        # Wait for events
        while not self.subscribed:
            time.sleep(1)

        logging.info("E2 Health Check Passed")
        return True

    def e2_message_handler(self, e2event):
        logging.info("Received E2 message: %s", e2event.data)

    def subscription_callback(self, sub_id, notification):
        logging.info("Received RIC subscription notification: %s", notification)
        self.subscribed = True

def perform_e2_health_check():
    try:
        e2_health_check = E2HealthCheck()
        result = e2_health_check.run()
        return result
    except RICXappException as e:
        logging.error(str(e))
        return False
