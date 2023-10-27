# subscription_manager.py
import logging
from ricxappframe.xapp_subscribe import NewSubscriber
import ricxappframe.subsclient as subsclient

class SubscriptionManager:
    def __init__(self, uri, local_address="0.0.0.0", local_port=8088):
        self.subscriptions = {}
        self.subscriber = NewSubscriber(uri=uri, local_address=local_address, local_port=local_port)
        self.logger = logging.getLogger(__name__)
        self.subscriber.ResponseHandler(responseCB=self.subscription_response_handler)

    def initialize_subscriptions(self):
        # Initialize your subscriptions here if needed
        pass

    def send_subscription_request(self, subscription_id, payload):
        try:
            action = subsclient.ActionToBeSetup(action_id=1, action_type="report")
            subscription_detail = subsclient.SubscriptionDetail(xapp_event_instance_id=subscription_id, action_to_be_setup_list=[action])
            params = subsclient.SubscriptionParams(subscription_id=subscription_id, subscription_details=[subscription_detail])
            
            response, reason, status = self.subscriber.Subscribe(subs_params=params)
            if status == 200:
                self.logger.info("Subscription request sent successfully for subscription ID: %s", subscription_id)
                self.subscriptions[subscription_id] = {'status': 'pending', 'payload': payload}
            else:
                self.logger.error("Failed to send subscription request for subscription ID: %s, Reason: %s, Status: %s", subscription_id, reason, status)
        except Exception as e:
            self.logger.error("An error occurred while sending subscription request for subscription ID: %s, Error: %s", subscription_id, str(e))

    def subscription_response_handler(self, data):
        try:
            self.logger.info("Received subscription response: %s", data)
            # Add logic to parse and handle the response data
        except Exception as e:
            self.logger.error("An error occurred while handling subscription response, Error: %s", str(e))

    def unsubscribe(self, subscription_id):
        try:
            if subscription_id in self.subscriptions:
                _, reason, status = self.subscriber.UnSubscribe(subs_id=str(subscription_id))
                if status == 200:
                    del self.subscriptions[subscription_id]
                    self.logger.info("Unsubscription successful for subscription ID: %s", subscription_id)
                else:
                    self.logger.error("Failed to unsubscribe for subscription ID: %s, Reason: %s, Status: %s", subscription_id, reason, status)
            else:
                self.logger.warning("Unknown subscription ID: %s", subscription_id)
        except Exception as e:
            self.logger.error("An error occurred while unsubscribing for subscription ID: %s, Error: %s", subscription_id, str(e))
