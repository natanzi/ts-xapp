# rmr_health_check.py
from ricxappframe.xapp_frame import RMRXapp
import logging

def default_handler(summary, sbuf):
    # You need to define the behavior of this handler
    pass

rmr_xapp = RMRXapp(default_handler, rmr_port=4560)

def rmr_health_check():
    logging.info("Executing RMR Health Check...")
    ok = rmr_xapp.healthcheck()
    if ok:
        return "OK: RMR Health check completed successfully and it's fine"
    else:
        return "ERROR: RMR is unhealthy"
