#A1PolicyManager.py
import logging
from ricxappframe.xapp_frame import RMRXapp
from constants import Constants

class A1PolicyManager:
    def __init__(self, rmr_xapp: RMRXapp):
        self._rmr_xapp = rmr_xapp
        self.logger = logging.getLogger(__name__)

    def startup(self):
        policy_query = '{"policy_type_id":"' + str(Constants.HELLOWORLD_POLICY_ID) + '"}'
        self._rmr_xapp.rmr_send(policy_query.encode(), Constants.A1_POLICY_QUERY)
        self.logger.info("A1PolicyManager.startup:: Sent A1 policy query = " + policy_query)
