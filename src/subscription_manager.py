#subscription_manager.py
import logging
import json
from ricxappframe.xapp_frame import RMRXapp

class SubscriptionManager:
    def __init__(self, rmr_xapp: RMRXapp):
        self.rmr_xapp = rmr_xapp
        self.subscriptions = {}  # A dictionary to store subscription information

    def get_gnb_list(self):
        # TODO: Implement the logic to retrieve gNB IDs
        # This is a placeholder list for demonstration
        return ['gnb1', 'gnb2', 'gnb3']
    
    def get_enb_list(self):
        # TODO: Implement the logic to retrieve eNB IDs
        # This is a placeholder list for demonstration
        return ['enb1', 'enb2', 'enb3']

    def send_subscription_request(self, xnb_id):
        subscription_id = xnb_id  # Using xnb_id as the subscription ID for simplicity
        msg_type = 13010  # RIC Subscription Request message type
        
        # Creating a sample payload for the subscription request
        payload = {
            "subscription_id": subscription_id,
            "xnb_id": xnb_id,
            # Add other necessary fields here
        }
        
        sbuf = self.rmr_xapp.rmr_alloc_msg(len(json.dumps(payload)))
        sbuf.contents.mtype = msg_type
        sbuf.contents.len = len(json.dumps(payload))
        sbuf.contents.payload = json.dumps(payload).encode('utf-8')
        self.rmr_xapp.rmr_send_msg(sbuf)
        
        logging.info("Subscription request sent for xnb ID: %s", xnb_id)
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
        
        sbuf = self.rmr_xapp.rmr_alloc_msg(len(json.dumps(payload)))
        sbuf.contents.mtype = msg_type
        sbuf.contents.len = len(json.dumps(payload))
        sbuf.contents.payload = json.dumps(payload).encode('utf-8')
        self.rmr_xapp.rmr_send_msg(sbuf)
        
        logging.info("Unsubscription request sent for subscription ID: %s", subscription_id)
        self.subscriptions[subscription_id]['status'] = 'unsubscribing'

    def handle_unsubscription_response(self, summary, sbuf):
        subscription_id = summary.get('subscription_id', 'Unknown')
        if subscription_id in self.subscriptions:
            result = summary.get('result', 'fail')
            if result == 'success':
                del self.subscriptions[subscription_id]
                logging.info("Unsubscription successful for subscription ID: %s", subscription_id)
            else:
                logging.error("Unsubscription failed for subscription ID: %s", subscription_id)
                # Handle the error as needed
        else:
            logging.warning("Received unsubscription response for unknown subscription ID: %s", subscription_id)

    def initialize_subscriptions(self):
        gnb_list = self.get_gnb_list()
        enb_list = self.get_enb_list()
        
        for gnb in gnb_list:
            self.send_subscription_request(gnb)
            
        for enb in enb_list:
            self.send_subscription_request(enb)
            
        logging.info("Subscriptions initialized")
