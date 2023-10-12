from mdclogpy import Logger, Level

class AppLogger:
    def __init__(self, name, verbose):
        self.loglevel = self.get_log_level(verbose)
        self.logger = Logger(name, self.loglevel)

    def get_log_level(self, verbose):
        loglevel = Level.INFO
        if verbose == 0:
            loglevel = Level.ERROR
        elif verbose == 1:
            loglevel = Level.WARNING
        elif verbose == 2:
            loglevel = Level.INFO
        elif verbose >= 3:
            loglevel = Level.DEBUG
        return loglevel

    def get_logger(self):
        return self.logger
