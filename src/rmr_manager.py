import rmr
import time
import logging

class RMRManager:
    def __init__(self, service, level, port="4560"):
        self.service = service
        self.level = level
        self.port = port
        self.rmr_context = None

    def initialize(self):
        logging.info('Initializing RMR')
        rmr_init_str = bytes(self.port, encoding='utf-8')
        self.rmr_context = rmr.rmr_init(rmr_init_str, rmr.RMR_MAX_RCV_BYTES, 0x00)
        while rmr.rmr_ready(self.rmr_context) == 0:
            logging.info('RMR not yet ready')
            time.sleep(1)
        rmr.rmr_set_stimeout(self.rmr_context, 1)
        rmr.rmr_set_vlevel(self.level)
        logging.info('RMR ready')

    def receive_messages(self):
        logging.info('Waiting for messages')
        while True:
            rmr_buffer = rmr.rmr_torcv_msg(self.rmr_context, None, 10000)
            summary = rmr.message_summary(rmr_buffer)
            if summary[rmr.RMR_MS_MSG_STATE] == 12:
                logging.info("No messages received within the timeout period")
            else:
                logging.info(f"Message received: {summary}")
                # Process the message here
            rmr.rmr_free_msg(rmr_buffer)

    def close(self):
        if self.rmr_context:
            rmr.rmr_close(self.rmr_context)
