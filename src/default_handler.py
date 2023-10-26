#default_handler.py
import logging
from ricxappframe.xapp_frame import rmr
from subscription_manager import SubscriptionManager

subscription_manager = None  # This will be set in your main application file

def set_subscription_manager(manager):
    global subscription_manager
    subscription_manager = manager

def handle_subscription_request(summary, sbuf):
    logging.info("Handling RIC Subscription Request")
    # Add your logic here to handle the subscription request

def handle_subscription_response(summary, sbuf):
    logging.info("Handling RIC Subscription Response")
    if subscription_manager:
        subscription_manager.handle_subscription_response(summary, sbuf)
    else:
        logging.error("Subscription manager is not set")

def handle_subscription_failure(summary, sbuf):
    logging.info("Handling RIC Subscription Failure")
    # Add your logic here to handle the subscription failure

def handle_subscription_delete_request(summary, sbuf):
    logging.info("Handling RIC Subscription Delete Request")
    # Add your logic here to handle the subscription delete request

def handle_subscription_delete_response(summary, sbuf):
    logging.info("Handling RIC Subscription Delete Response")
    if subscription_manager:
        subscription_manager.handle_unsubscription_response(summary, sbuf)
    else:
        logging.error("Subscription manager is not set")

def handle_subscription_delete_failure(summary, sbuf):
    logging.info("Handling RIC Subscription Delete Failure")
    # Add your logic here to handle the subscription delete failure

def default_rmr_handler(summary, sbuf):
    """
    Default handler function for processing RMR messages.

    :param summary: A dictionary containing information about the received message.
    :param sbuf: The received RMR message buffer.
    """
    msg_type = summary.get('mtype', 'Unknown')
    msg_state = summary.get('state', 'Unknown')
    transaction_id = summary.get('xid', 'Unknown')

    logging.info(f"Received RMR message - Type: {msg_type}, State: {msg_state}, Transaction ID: {transaction_id}")

    if msg_type == 12010:  # RIC Subscription Request
        handle_subscription_request(summary, sbuf)
    elif msg_type == 12011:  # RIC Subscription Response
        handle_subscription_response(summary, sbuf)
    elif msg_type == 12012:  # RIC Subscription Failure
        handle_subscription_failure(summary, sbuf)
    elif msg_type == 12013:  # RIC Subscription Delete Request
        handle_subscription_delete_request(summary, sbuf)
    elif msg_type == 12014:  # RIC Subscription Delete Response
        handle_subscription_delete_response(summary, sbuf)
    elif msg_type == 12015:  # RIC Subscription Delete Failure
        handle_subscription_delete_failure(summary, sbuf)
    else:
        # Handle other message types as needed
        pass

    # Accessing and logging the payload of the message
    payload = sbuf.get_payload()
    logging.info(f"Message payload: {payload}")

    # Freeing the RMR message buffer
    sbuf.contents.state = 0  # Resetting the state before freeing
    rmr.rmr_free_msg(sbuf)
