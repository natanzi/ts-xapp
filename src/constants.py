#constants.py
#These constants are used when sending and receiving messages over the A1 interface, among other things
class Constants:
    A1_POLICY_QUERY = 20012
    HELLOWORLD_POLICY_ID = 2
    RIC_HEALTH_CHECK_REQ = 100
    RIC_HEALTH_CHECK_RESP = 101
    A1_POLICY_REQ = 20010
    A1_POLICY_RESP = 20011
    RIC_ALARM_UPDATE = 110
    ACTION_TYPE = "REPORT"
    SUBSCRIPTION_PATH = "http://service-{}-{}-http:{}"
    PLT_NAMESPACE = "ricplt"
    SUBSCRIPTION_SERVICE = "submgr"
    SUBSCRIPTION_PORT = "3800"
    SUBSCRIPTION_REQ = 12011
    A1_HEALTH_CHECK_REQ = 30010
    A1_HEALTH_CHECK_RESP = 30011
