"""
Handles subscription messages from enbs and gnbs through rmr.
"""
import json
from ricxappframe.xapp_frame import RMRXapp, rmr
# Assuming _BaseHandler is defined in your project, adjust the import as necessary
from ._BaseHandler import _BaseHandler  

class SubscriptionHandler(_BaseHandler):

    def __init__(self, rmr_xapp: RMRXapp, msgtype):
        super().__init__(rmr_xapp, msgtype)

    def request_handler(self, rmr_xapp, summary, sbuf):
        """
        Handles subscription messages.

        Parameters
        ----------
        rmr_xapp: rmr Instance Context
        summary: dict (required)
            buffer content
        sbuf: str (required)
            length of the message
        """
        self._rmr_xapp.rmr_free(sbuf)
        try:
            req = json.loads(summary[rmr.RMR_MS_PAYLOAD])  # input should be a json encoded as bytes
            self.logger.debug("SubscriptionHandler.request_handler:: Handler processing request")
        except (json.decoder.JSONDecodeError, KeyError):
            self.logger.error("SubscriptionHandler.request_handler:: Handler failed to parse request")
            return

        if self.verifySubscription(req):
            self.logger.info("SubscriptionHandler.request_handler:: Handler processed request: {}".format(req))
        else:
            self.logger.error("SubscriptionHandler.request_handler:: Request verification failed: {}".format(req))
            return
        self.logger.debug("SubscriptionHandler.request_handler:: Request verification success: {}".format(req))

    def verifySubscription(self, req: dict):
        """
        Verifies the subscription request.

        Parameters
        ----------
        req: dict
            The subscription request to verify.

        Returns
        -------
        bool
            True if the subscription request is valid, False otherwise.
        """
        for i in ["subscription_id", "message"]:
            if i not in req:
                return False
        return True

    # Define additional methods as needed for TS xApp's subscription management
    # For example, methods to subscribe, unsubscribe, handle notifications, etc.

# End of SubscriptionHandler class
