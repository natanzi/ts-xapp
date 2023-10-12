import json
import ricxappframe.xapp_subscribe as subscribe

class SubscriptionManager:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.subscriber = None
        self.subsCfgDetail = self.GetSubsConfig()
        if self.subsCfgDetail:
            self.subscriber = subscribe.NewSubscriber(self.subsCfgDetail['url'] + 'ric/v1')

    def GetSubsConfig(self):
        if self.config.cfg['controls'].get('subscription'):
            return self.config.cfg['controls'].get('subscription')

    def Subscribe(self, subObj):
        if self.subscriber:
            self.logger.info("Sending the subscription to %s" % (self.subsCfgDetail['url'] + 'ric/v1'))
            self.logger.info(subObj.to_dict())
            data, reason, status = self.subscriber.Subscribe(subObj)
            self.logger.info("Getting the subscription response")
            self.logger.info(json.loads(data))

    def Unsubscribe(self, subscription_id):
        if self.subscriber:
            reason, status = self.subscriber.UnSubscribe(subscription_id)

    def QuerySubscriptions(self):
        if self.subscriber:
            data, reason, status = self.subscriber.QuerySubscriptions()
