import time
import rmr
from ricxappframe.xapp_frame import RMRXapp

class RMRManager:
    def __init__(self, service, level, logger):
        self.service = service
        self.level = level
        self.logger = logger
        self.rmr_mrc = None
        self.init_rmr()

    def init_rmr(self):
        data = None
        os.environ["RMR_SRC_ID"] = self.service
        os.environ["RMR_LOG_VLEVEL"] = str(self.level)
        os.environ["RMR_RTG_SVC"] = "4561"
        # ... (rest of the RMR initialization code)
        self.rmrInit(b"4560")

    def rmrInit(self, initbind):
        self.rmr_mrc = rmr.rmr_init(initbind, rmr.RMR_MAX_RCV_BYTES, 0x00)
        while rmr.rmr_ready(self.rmr_mrc) == 0:
            time.sleep(1)
            self.logger.info('RMR not yet ready')
        rmr.rmr_set_stimeout(self.rmr_mrc, 1)
        rmr.rmr_set_vlevel(5)
        self.logger.info('RMR ready')

    def receive_message(self):
        while True:
            print("Waiting for a message, will timeout after 10s")
            rmr_sbuf = rmr.rmr_torcv_msg(self.rmr_mrc, None, 10000)
            summary = rmr.message_summary(rmr_sbuf)
            if summary[rmr.RMR_MS_MSG_STATE] == 12:
                print("Nothing received")
            else:
                print("Message received!: {}".format(summary))
                data = rmr.get_payload(rmr_sbuf)
            rmr.rmr_free_msg(rmr_sbuf)
