from helpers.bithumb_api import BithumbGlobalRestAPI
from config import get_cfg

cfg = get_cfg('bithumb')
bh = BithumbGlobalRestAPI(cfg['key'], cfg['secret'])


def get_all_pairs_list():
    all_pairs = bh.all_pairs()
    pairs = []
    for pair in all_pairs:
        pairs.append(pair['symbol'])

    return pairs