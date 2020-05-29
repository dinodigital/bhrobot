import time

from pyrogram import Client, Filters, Message

from helpers.db import create_user, db_save
from helpers.main_msg import new_main_msg
from helpers.telegram import send_message
from _interface.messages import input_api_key_msg, gen_creds_msg
from models import User


@Client.on_message(~Filters.bot & Filters.command("start"))
def start(bot: Client, m: Message):
    tg_id = m.from_user.id
    user = User.get_or_none(tg_id=tg_id)

    m.delete()

    if user is None:
        user = create_user(m)
        r = send_message(bot, tg_id, gen_creds_msg(user, input_msg=input_api_key_msg))
        user.msg_ids['b_main'] = r.message_id
        db_save(user)
        return

    elif not user.secret:
        bot.delete_messages(tg_id, user.msg_ids['b_main'])
        r = send_message(bot, tg_id, gen_creds_msg(user, input_msg=input_api_key_msg))
        user.msg_ids['b_main'] = r.message_id
        db_save(user)
        return

    new_main_msg(user, bot)
    return



