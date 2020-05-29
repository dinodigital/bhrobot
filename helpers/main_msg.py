from pyrogram import Client

from _interface.inline_markups import main_menu, refresh_main_btn
from _interface.messages import err_creds, input_api_key_msg, gen_main_msg, gen_err_msg, connecting_msg, err
from helpers.bithumb import get_balance
from helpers.db import db_save
from helpers.telegram import send_message, edit_message
from models import User


def new_main_msg(user: User, bot: Client):
    main_msg_id = user.msg_ids['b_main']

    # Обновляем главное сообщение
    bot.delete_messages(user.tg_id, main_msg_id)
    r = send_message(bot, user.tg_id, connecting_msg)

    user.msg_ids['b_main'] = msg_id = r.message_id
    db_save(user)

    response = get_balance(user.api_key, user.secret)
    connected = response[0]

    # Авторизован на Bithumb, есть балансы
    if connected:
        edit_message(bot, user.tg_id, msg_id, gen_main_msg(response), reply_markup=refresh_main_btn())

    # Ошибка авторизации
    else:
        err_code = response[1]  # Код ошибки
        err_msg = response[2]  # Текст ошибки
        if err_code == '9000' or err_code == '9002':
            user.api_key = ''
            user.secret = ''
            edit_message(bot, user.tg_id, msg_id, gen_err_msg(err_creds, input_msg=input_api_key_msg))
            db_save(user)
        else:
            edit_message(bot, user.tg_id, msg_id, gen_err_msg(err + err_msg, input_msg="Try again"))

    return
