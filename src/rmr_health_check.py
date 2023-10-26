# rmr_health_check.py
from ricxappframe.xapp_frame import RMRXapp
import logging

def rmr_health_check(rmr_xapp):
    logging.info("Executing RMR Health Check...")
    ok = rmr_xapp.healthcheck()
    if ok:
        return "OK: RMR Health check completed successfully and it's fine"
    else:
        return "ERROR: RMR is unhealthy"
