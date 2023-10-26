#default_handler.py
import logging

def default_rmr_handler(summary, sbuf):
    """
    Default handler function for processing RMR messages.

    :param summary: A dictionary containing information about the received message.
    :param sbuf: The received RMR message buffer.
    """
    # Extracting message details from the summary
    msg_type = summary.get('mtype', 'Unknown')
    msg_state = summary.get('state', 'Unknown')
    transaction_id = summary.get('xid', 'Unknown')

    # Logging the received message details
    logging.info(f"Received RMR message - Type: {msg_type}, State: {msg_state}, Transaction ID: {transaction_id}")

    # Accessing and logging the payload of the message
    payload = sbuf.get_payload()
    logging.info(f"Message payload: {payload}")

    # Add any additional logic you need for handling messages here

    # If needed, you can send a response back using the rmr.rmr_send_msg function
    # response_sbuf = rmr.rmr_alloc_msg(rmr_xapp.rmr_ctx, 256)
    # response_sbuf.contents.mtype = <response_message_type>
    # response_sbuf.contents.len = len(response_payload)
    # response_sbuf.contents.payload = response_payload
    # rmr.rmr_send_msg(rmr_xapp.rmr_ctx, response_sbuf)

    # Freeing the RMR message buffer
    sbuf.contents.state = 0  # Resetting the state before freeing
    rmr.rmr_free_msg(sbuf)

# If you want to test the default handler independently, you can add a main function here
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Testing the default RMR handler")
    
    # You would need to set up a mock summary and sbuf for testing
    # summary = {'mtype': 10000, 'state': 0, 'xid': '12345'}
    # sbuf = ...
    # default_rmr_handler(summary, sbuf)
