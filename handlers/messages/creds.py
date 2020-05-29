import time

from pyrogram import Client, Message, Filters

from _interface.inline_markups import refresh_main_btn
from _interface.messages import input_secret_msg, gen_creds_msg, err_creds, input_api_key_msg, gen_err_msg, gen_main_msg
from handlers.filters import api_key_input_filter, secret_input_filter
from helpers.bithumb import get_balance
from helpers.db import db_save
from helpers.security import encr
from helpers.telegram import edit_message
from models import User


@Client.on_message(~Filters.bot & api_key_input_filter)
def step_1(bot: Client, m: Message):
    """
    Обработчик присланного API ключа
    """
    user = User.get(tg_id=m.from_user.id)
    user.api_key = encr(m.text)
    db_save(user)

    # Удаляем сообщение с API ключем
    m.delete()

    # Уведомляем о получении ключа
    msg_id = user.msg_ids['b_main']
    edit_message(bot, user.tg_id, msg_id, gen_creds_msg(user, input_msg=input_secret_msg))

    return


@Client.on_message(~Filters.bot & secret_input_filter)
def step_2(bot: Client, m: Message):
    """
    Обрабатывает Secret
    Запрашивает и выводит балансы
    """
    tg_id = m.from_user.id
    user = User.get(tg_id=m.from_user.id)

    # Сохраняем secret ключ в БД
    user.secret = encr(m.text)
    db_save(user)

    # Удаляем сообщения
    m.delete()

    # Уведомляем о получении ключа
    msg_id = user.msg_ids['b_main']
    edit_message(bot, tg_id, msg_id, gen_creds_msg(user, status='connecting'))

    response = get_balance(user.api_key, user.secret)
    connected = response[0]

    msg_id = user.msg_ids['b_main']
    if connected:
        edit_message(bot, tg_id, msg_id, gen_main_msg(response), reply_markup=refresh_main_btn())

    else:
        err_code = response[1]
        err_msg = response[2]
        if err_code == '9000' or err_code == '9002':
            user.api_key = ''
            user.secret = ''
            bot.edit_message_text(tg_id, msg_id, gen_err_msg(err_creds, input_msg=input_api_key_msg))
            db_save(user)

    return
