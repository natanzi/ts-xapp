import json
import logging

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.configuration = None

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.configuration = json.load(file)
                logging.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")

    def get_config_item(self, key):
        if self.configuration and key in self.configuration:
            return self.configuration[key]
        return None
