import re

from pyrogram import Message, Filters, CallbackQuery
from models import User


def api_key_input(_, message: Message):
    """
    Юзер прислал api key
    """
    user = User.get(tg_id=message.from_user.id)
    return True if not user.api_key and not user.secret else False


def secret_input(_, message: Message):
    """
    Юзер прислал Secret key
    """
    user = User.get(tg_id=message.from_user.id)
    return True if user.api_key and not user.secret else False


def has_keys(_, message: Message):
    """
    API и секретный ключ есть в базе
    """
    user = User.get(tg_id=message.from_user.id)
    return True if user.api_key and user.secret else False


def user_none(_, message: Message):
    user = User.get_or_none(tg_id=message.from_user.id)
    return True if user is None else False


def buy_btc_f(_, q: CallbackQuery):
    return True if q.data == 'buy_btc' else False


def refresh_f(_, q: CallbackQuery):
    return True if q.data == 'refresh_main' else False


def is_full_order(_, message: Message):
    """
    True, если соответствует одному из написаний:
    /buy BTC for 1 USDT at 9000
    /buy 1 BTC for USDT at 9000
    """
    text = message.text
    buy_for_x = re.match(
        r'^/buy\s[a-zA-Z]+\sfor\s(\d|\d.\d)+\s[a-zA-Z]+\sat\s(\d|\d.\d)+'  # /buy BTC for 1 USDT at 9000
        r'(\s[+|-](\d|\d.\d)+%*)*(\s[+|-](\d|\d.\d)+%*)*$',  # Stop-loss, take-profit
        text)
    buy_x_for = re.match(
        r'^/buy\s(\d|\d.\d)+\s[a-zA-Z]+\sfor\s[a-zA-Z]+\sat\s(\d|\d.\d)+'  # /buy 1 BTC for USDT at 9000
        r'(\s[+|-](\d|\d.\d)+%*)*(\s[+|-](\d|\d.\d)+%*)*$',  # Stop-loss, take-profit
        text)

    matches = buy_for_x or buy_x_for

    return True if matches is not None else False


def is_market_order(_, message: Message):
    """
    True, если соответствует одному из написаний:
    /buy 0.001 BTC for USDT
    /buy BTC for 1 USDT
    """
    text = message.text
    mbuy_for_x = re.compile('^/buy\s[a-zA-Z]+\sfor\s(\d|\d.\d)+\s[a-zA-Z]+$')
    mbuy_x_for = re.compile('^/buy\s(\d|\d.\d)+\s[a-zA-Z]+\sfor\s[a-zA-Z]+$')

    matches = mbuy_for_x.search(text) or mbuy_x_for.search(text)

    return True if matches is not None else False


def hide_f(_, q: CallbackQuery):
    cmd = q.data.split('_')
    return True if cmd[0] == 'hide' else False


api_key_input_filter = Filters.create(api_key_input)
secret_input_filter = Filters.create(secret_input)
auth_filter = Filters.create(has_keys)
refresh_filter = Filters.create(refresh_f)
buy_btc_filter = Filters.create(buy_btc_f)
is_full_order_filter = Filters.create(is_full_order)
is_market_order_filter = Filters.create(is_market_order)
hide_filter = Filters.create(hide_f)
user_none_filter = Filters.create(user_none)
