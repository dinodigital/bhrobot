import time
from pprint import pprint

from pyrogram import Client, Filters, Message

from _interface.inline_markups import full_order_create_btns
from _interface.messages import buy_full_order_msg, gen_err_msg
from config import MAX_ACTIVE_ORDERS
from handlers.filters import is_full_order_filter, is_market_order_filter
from helpers.db import db_save
from helpers.orders import parse_full_order_data
from helpers.telegram import send_message
from models import User


@Client.on_message(~Filters.bot & Filters.command("buy") & is_full_order_filter)
def full_order(bot: Client, m: Message):
    user = User.get(tg_id=m.from_user.id)

    # Не авторизован
    if not user.api_key or not user.secret:
        return

    # Удаляем старые сообщения юзера и бота, если юзер присал новое
    if user.temp:
        bot.delete_messages(user.tg_id, user.temp['msg_ids'])

    # Лимит активных ордеров
    if user.orders_count >= MAX_ACTIVE_ORDERS:
        r = send_message(bot, user.tg_id, f'⚠️ <b>Alpha limit</b>\nYou can have only {MAX_ACTIVE_ORDERS} active order in alpha version of ths bot.\n\n<i>PM @gorbunov if you need more active orders.</i>')
        user.temp['msg_ids'] = [m.message_id, r.message_id]
        user.temp['text'] = m.text
        db_save(user)
        return

    # Обработчик ошибок пользователя
    params = parse_full_order_data(m.text)
    if type(params) is tuple:
        err_msg = params[1]
        r = send_message(bot, user.tg_id, gen_err_msg(f'🔴 <b>Error</b>\n{err_msg}'))
        user.temp['msg_ids'] = [m.message_id, r.message_id]
        db_save(user)
        return

    # Генерация сообщения с ордером
    msg = buy_full_order_msg(params)
    markup = full_order_create_btns()
    r = send_message(bot, user.tg_id, msg, reply_markup=markup)

    # Сохраняем id временных сообщений в базу
    user.temp['msg_ids'] = [m.message_id, r.message_id]
    user.temp['text'] = m.text
    db_save(user)


@Client.on_message(~Filters.bot & Filters.command("buy") & is_market_order_filter)
def market_order(bot: Client, m: Message):
    print('Market ордер')
    # print(m)
