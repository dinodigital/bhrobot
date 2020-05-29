from decimal import Decimal
from pprint import pprint

from retry import retry

from _interface.inline_markups import full_order_active_btns
from _interface.messages import active_order_msg, get_symbol
from data.pairs import pairs
from helpers.rex import is_buy_for_x, is_buy_x_for
from helpers.telegram import edit_message


def parse_full_order_data(text):
    cmd = text.split(' ')

    price = Decimal(cmd[6])
    symbol, is_reversed = get_symbol(text)
    if not is_reversed:
        side = 'buy'
        quantity = Decimal(cmd[1]) if is_buy_x_for(text) else Decimal(cmd[3]) / price
    else:
        side = 'sell'
        quantity = Decimal(cmd[3]) if is_buy_for_x(text) else Decimal(cmd[1]) / price

    # User errors
    err_msg = ''
    if not symbol:
        err_msg = 'No such trading pair'
    elif quantity < Decimal(pairs[symbol]):
        err_msg = f'{symbol.split("-")[0]} quantity must be >= {pairs[symbol]}'
    elif price <= 0:
        err_msg = 'Price must be > 0'
    if err_msg:
        return False, err_msg

    return {
        'symbol': symbol,
        'type': 'limit',
        'side': side,
        'price': price,
        'quantity': quantity
    }


@retry(tries=3, delay=1, backoff=2)
def refresh_order_msg(order, bh, bot, user):
    current_price = bh.get_current_price(order.pair, order.side)
    msg = active_order_msg(order.text, current_price)
    markup = full_order_active_btns()
    edit_message(bot, user.tg_id, order.b_msg_id, msg, reply_markup=markup)


# text = '/buy 100 BIP for USDT at 0.001'
# print(text)
# params = parse_full_order_data(text)
# if params:
#     print(bh.place_order_2(params))
