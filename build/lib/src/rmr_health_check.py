from ricxappframe.xapp_frame import RMRXapp
import ricxappframe.rmr.rmr_constants as rmrC

class RMRHealthCheckXapp(RMRXapp):
    def __init__(self):
        super().__init__()

    def rmr_health_check(self):
        try:
            # Send a health check message
            summary, _ = self.rmr_send(rmrC.MT_HEALTH_CHECK_REQ, b"Health Check")

            # Check if the message was sent successfully
            if summary[0] == rmrC.RMR_OK:
                print("RMR Health Check: PASS")
            else:
                print(f"RMR Health Check: FAIL - {summary[1]}")

        except Exception as e:
            print(f"RMR Health Check: EXCEPTION - {str(e)}")

# If running this file directly, execute the RMR health check
if __name__ == "__main__":
    xapp = RMRHealthCheckXapp()
    xapp.rmr_health_check()

