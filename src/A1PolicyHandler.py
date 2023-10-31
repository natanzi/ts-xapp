#A1PolicyHandler.py
from ricxappframe.xapp_frame import RMRXapp
import json
import logging

class A1PolicyHandler:
    def __init__(self, rmr_xapp: RMRXapp):
        self._rmr_xapp = rmr_xapp
        self.logger = logging.getLogger(__name__)

    def request_handler(self, summary, sbuf):
    self._rmr_xapp.rmr_free(sbuf)
    try:
        req = json.loads(summary['payload'])  # input should be a json encoded as bytes
        self.logger.debug("A1PolicyHandler.request_handler:: Handler processing request")
    except (json.decoder.JSONDecodeError, KeyError):
        self.logger.error("A1PolicyHandler.request_handler:: Handler failed to parse request")
        return

    if self.verifyPolicy(req):
        self.logger.info("A1PolicyHandler.request_handler:: Handler processed request: {}".format(req))
    else:
        self.logger.error("A1PolicyHandler.request_handler:: Request verification failed: {}".format(req))
        return
    self.logger.debug("A1PolicyHandler.request_handler:: Request verification success: {}".format(req))

    resp = self.buildPolicyResp(req)
    self._rmr_xapp.rmr_send(json.dumps(resp).encode(), Constants.A1_POLICY_RESP)
    self.logger.info("A1PolicyHandler.request_handler:: Response sent: {}".format(resp))
    
    def verifyPolicy(self, req: dict):
        for i in ["policy_type_id", "operation", "policy_instance_id"]:
            if i not in req:
                return False
        return True

    def buildPolicyResp(self, req: dict):
        req["handler_id"] = self._rmr_xapp.config["xapp_name"]
        del req["operation"]
        req["status"] = "OK"
        return req
