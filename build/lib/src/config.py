import json
import logging

class Config:
    def __init__(self, xapp_name, config_file):
        self.config_file = config_file
        self.xapp_name = xapp_name
        self.cfg = None
        self.keys = dict()
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                cfg = file.read()
                if cfg:
                    self.cfg = json.loads(cfg)
                    if self.cfg:
                        self.controls = self.cfg.get('controls', {})
        except Exception as e:
            logging.error(f"Error loading config file {self.config_file}: {str(e)}")

    def get_key_item(self, key):
        return self.keys.get(key)

    def get_config(self):
        # ... (existing method implementation)
        pass
