#subscription_manager.py
import logging
from ricxappframe.xapp_frame import rmr

class SubscriptionManager:
    def __init__(self, rmr_xapp):
        self.rmr_xapp = rmr_xapp
        self.subscriptions = {}  # A dictionary to store subscription information
    
    def send_subscription_request(self, subscription_id, payload):
        msg_type = 13010  # RIC Subscription Request message type
        sbuf = self.rmr_xapp.rmr_alloc_msg(len(payload))
        sbuf.contents.mtype = msg_type
        sbuf.contents.len = len(payload)
        sbuf.contents.payload = payload
        self.rmr_xapp.rmr_send_msg(sbuf)
        
        logging.info("Subscription request sent for subscription ID: %s", subscription_id)
        self.subscriptions[subscription_id] = {'status': 'pending', 'payload': payload}

    def handle_subscription_response(self, summary, sbuf):
        subscription_id = summary.get('subscription_id', 'Unknown')
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id]['status'] = 'subscribed'
            logging.info("Subscription successful for subscription ID: %s", subscription_id)
        else:
            logging.warning("Received subscription response for unknown subscription ID: %s", subscription_id)

    def send_unsubscription_request(self, subscription_id):
        if subscription_id not in self.subscriptions:
            logging.warning("Cannot unsubscribe. Unknown subscription ID: %s", subscription_id)
            return

        msg_type = 13013  # RIC Subscription Delete Request message type
        payload = self.subscriptions[subscription_id]['payload']
        
        sbuf = self.rmr_xapp.rmr_alloc_msg(len(payload))
        sbuf.contents.mtype = msg_type
        sbuf.contents.len = len(payload)
        sbuf.contents.payload = payload
        self.rmr_xapp.rmr_send_msg(sbuf)
        
        logging.info("Unsubscription request sent for subscription ID: %s", subscription_id)
        self.subscriptions[subscription_id]['status'] = 'unsubscribing'

    def handle_unsubscription_response(self, summary, sbuf):
        subscription_id = summary.get('subscription_id', 'Unknown')
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            logging.info("Unsubscription successful for subscription ID: %s", subscription_id)
        else:
            logging.warning("Received unsubscription response for unknown subscription ID: %s", subscription_id)


