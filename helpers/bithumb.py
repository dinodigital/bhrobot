from decimal import Decimal

from helpers.bithumb_api import BithumbGlobalRestAPI


def pretty_round(x):
    x = Decimal(str(x))
    if x >= 1 and x % int(x) == 0:
        return int(x)
    elif x > 1:
        return round(x, 1)
    elif x >= 0.1:
        return round(x, 2)
    elif x >= 0.01:
        return round(x, 3)
    elif x >= 0.001:
        return round(x, 4)
    elif x >= 0.0001:
        return round(x, 5)
    elif x >= 0.00001:
        return round(x, 6)
    else:
        return round(x, 7)


def get_balance(key, secret):
    try:
        bh = BithumbGlobalRestAPI(key, secret)
        all_balances = bh.balance()

        good_balance = {}
        btc_balance = 0
        for balance in all_balances:
            qty = Decimal(balance['btcQuantity'])

            if qty > 0:
                btc_balance += qty

                coin = balance['coinType']
                count = Decimal(balance['count'])
                frozen = Decimal(balance['frozen'])
                coin_total = count + frozen
                btc_total = qty

                good_balance[coin] = {'coin_total': coin_total, 'btc_total': btc_total, 'frozen': frozen, 'count': count}

        return True, btc_balance, good_balance

    except Exception as e:
        return False, e.code, e.msg


def bh_publish_order(bh, params):
    try:
        accuracy = get_accuracy(bh, params['symbol'])
        params['quantity'] = round(params['quantity'], accuracy[0])
        return bh.place_order_2(params)
    except Exception as e:
        return False, e.msg


def get_accuracy(bh, pair):
    """
    Получем значение округления по паре
    """
    pairs = bh.all_pairs()

    for i in pairs:
        if i['symbol'] == pair:
            return [int(x) for x in i['accuracy'][::-1]]
