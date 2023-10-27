#default_handler.py
import logging
from ricxappframe.xapp_frame import rmr

# Create a global variable to hold the subscription manager instance
subscription_manager = None

def set_subscription_manager(manager):
    """
    Set the subscription manager instance.

    :param manager: An instance of the SubscriptionManager class.
    """
    global subscription_manager
    subscription_manager = manager

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

    # Accessing and logging the payload of the message
    payload = sbuf.get_payload()
    logging.info(f"Message payload: {payload}")

    # You can now use the subscription_manager here if needed
    if subscription_manager is not None:
        # Add your logic here to interact with the subscription manager
        pass

    # Freeing the RMR message buffer
    sbuf.contents.state = 0  # Resetting the state before freeing
    rmr.rmr_free_msg(sbuf)
