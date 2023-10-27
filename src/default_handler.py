#default_handler.py
import logging
from ricxappframe.xapp_frame import rmr

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

    # Freeing the RMR message buffer
    sbuf.contents.state = 0  # Resetting the state before freeing
    rmr.rmr_free_msg(sbuf)
