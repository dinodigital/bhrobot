from configparser import ConfigParser

MAX_ACTIVE_ORDERS = 3

cfg_parser = ConfigParser()
cfg_parser.read('config.ini')


def get_cfg(name):
    return cfg_parser[name]
