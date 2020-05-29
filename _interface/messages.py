from datetime import datetime
from decimal import Decimal

from data.pairs import pairs
from helpers.bithumb import pretty_round
from helpers.rex import is_buy_x_for, is_buy_for_x

input_api_key_msg = '⚠️ Send Bithumb <a href="https://www.bithumb.pro/en-us/account/user/api-key/list">API</a> key️'
input_secret_msg = '⚠️ Send Bithumb <a href="https://www.bithumb.pro/en-us/account/user/api-key/list">Secret</a> key'

err_creds = "🔴️ <b>Connection Error</b>\nInvalid API key or Secret key"
err = "🔴️ <b>Error</b>\n"

connecting_msg = f'🔐 Connecting to Bithumb...'


def gen_creds_msg(user, input_msg=None, err_msg=None, status=None):
    connection_icon = '⚙️' if err_msg is None else '🔴'
    api_icon = '✅' if user.api_key else '❔'
    secret_icon = '✅️' if user.secret else '❔'

    if status == 'connecting':
        msg = connecting_msg
    else:
        msg = f'{connection_icon} <b>Bithumb Global</b>'

    msg += f'\n├ {api_icon} API key'
    msg += f'\n└ {secret_icon} Secret key'

    if err_msg is not None:
        msg += f'\n\n{err_msg}'

    if input_msg is not None:
        msg += f'\n\n{input_msg}'

    return msg


def gen_err_msg(err_msg, input_msg=None):
    msg = err_msg

    if input_msg is not None:
        msg += f'\n\n{input_msg}'

    return msg


def write_coin_balances(coins):
    """
    Красиво печатает балансы монет
    """
    msg = ''
    for i, coin in enumerate(coins, 1):
        msg += '\n'
        msg += '└ ' if i == len(coins) else '├ '
        msg += f'{coin}: {coins[coin]["coin_total"]}'

    return msg


def gen_main_msg(balances):
    icon = '🟢️'

    msg = f'{icon} <b>Bithumb Global</b>\n'
    msg += f'└ <i>Refreshed {datetime.strftime(datetime.now(), "%d %b at %H:%M")}</i>'

    msg += f'\n\n💰<b>{balances[1]} BTC</b>'
    msg += write_coin_balances(balances[2])

    return msg


def buy_full_order_msg(params):
    """
    params = {
        'symbol': symbol,
        'type': 'limit',
        'side': side,
        'price': price,
        'quantity': quantity
    }
    """
    side = params['side']
    pair = params['symbol']
    price = params['price']
    x = params['quantity']
    split = pair.split('-')

    if side == 'buy':
        buy, sell = split[0], split[1]
        msg = '✳️ <b>Buy order</b>\n\n'
    else:
        sell, buy = split[0], split[1]
        msg = '🔻 <b>Sell order</b>\n\n'

    msg += f'<b>Pair:</b> {pair}\n'
    msg += f'<b>Price:</b> {price}\n'
    msg += f'<b>Buy:</b> {pretty_round(x)} {buy}\n' if side == 'buy' else f'<b>Buy:</b> {pretty_round(x * price)} {buy}\n'
    msg += f'<b>Sell:</b> {pretty_round(x * price)} {sell}\n' if side == 'buy' else f'<b>Sell:</b> {pretty_round(x)} {sell}\n'

    return msg


def active_order_msg(text, current_price):

    cmd = text.split(' ')

    pair, is_reversed = get_symbol(text)
    price = Decimal(cmd[6])
    split = pair.split('-')

    if not is_reversed:
        # BUY
        if is_buy_x_for(text):
            qty1 = Decimal(cmd[1])
            qty2 = qty1 * price
        else:
            qty2 = Decimal(cmd[3])
            qty1 = qty2 / price
        msg = f'✳️ <b>Buy {pretty_round(qty1)} {split[0]} for {pretty_round(qty2)} {split[1]}</b>\n\n'
    else:
        # SELL
        if is_buy_for_x(text):
            qty1 = Decimal(cmd[3])
            qty2 = qty1 * price
        else:
            qty2 = Decimal(cmd[1])
            qty1 = qty2 / price
        msg = f'🔻 <b>Sell {pretty_round(qty1)} {split[0]} for {pretty_round(qty2)} {split[1]}</b>\n\n'

    msg += f'<b>Target price</b>: {price}\n'
    msg += f'<b>Current price</b>: {pretty_round(current_price)}\n\n'

    msg += f'<i>Refreshed {datetime.strftime(datetime.now(), "%d %b at %H:%M")}</i>'

    return msg


def get_symbol(text):
    """
    Gets API symbol from 2 crypto coins
    :return: symbol, is_reversed
    If is_reversed == 1, then coins switched their places (USDT-BTC -> BTC-USDT)
    """
    cmd = text.split(' ')
    cmd[0] = cmd[0][1:]

    coin_1 = cmd[1].upper() if is_buy_for_x(text) else cmd[2].upper()
    coin_2 = cmd[4].upper()

    pair_1 = f'{coin_1}-{coin_2}'
    pair_2 = f'{coin_2}-{coin_1}'

    if pair_1 in pairs:
        return pair_1, 0
    elif pair_2 in pairs:
        return pair_2, 1
    else:
        return '', ''


def completed_order_msg(order):
    pair = order.pair
    split = pair.split('-')

    if order.side == 'buy':
        return f'✅ Bought {order.quantity} {split[0]} for {split[1]} at price {order.price}'
    elif order.side == 'sell':
        return f'✅ Sold {order.quantity} {split[0]} for {split[1]} at price {order.price}'


def cancelled_order_msg(text):

    cmd = text.split(' ')

    pair, is_reversed = get_symbol(text)
    price = Decimal(cmd[6])
    split = pair.split('-')

    if not is_reversed:
        # BUY
        if is_buy_x_for(text):
            qty1 = Decimal(cmd[1])
            qty2 = qty1 * price
        else:
            qty2 = Decimal(cmd[3])
            qty1 = qty2 / price
        msg = f'🚫 <b>Buy {pretty_round(qty1)} {split[0]} for {pretty_round(qty2)} {split[1]}</b>\n\n'
    else:
        # SELL
        if is_buy_for_x(text):
            qty1 = Decimal(cmd[3])
            qty2 = qty1 * price
        else:
            qty2 = Decimal(cmd[1])
            qty1 = qty2 / price
        msg = f'🔻 <b>Sell {pretty_round(qty1)} {split[0]} for {pretty_round(qty2)} {split[1]}</b>\n\n'

    msg += f'Order was <b>cancelled</b> on Exchange'

    return msg