from pyrogram import Message
from retry import retry

from _interface.inline_markups import full_order_active_btns
from _interface.messages import active_order_msg


def handle_username(message):
    """
    Возвращает username или пустую строку, если username не задан
    """
    username = message.from_user.username
    return username if username is not None else ""


@retry(tries=3, delay=1, backoff=2)
def send_message(bot, tg_id, msg, reply_markup=None) -> Message:
    if reply_markup is not None:
        return bot.send_message(
            tg_id, msg, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
    else:
        return bot.send_message(
            tg_id, msg, parse_mode="HTML", disable_web_page_preview=True)


@retry(tries=3, delay=1, backoff=2)
def edit_message(bot, tg_id, msg_id, msg, reply_markup=None) -> Message:
    if reply_markup is not None:
        return bot.edit_message_text(
            tg_id, msg_id, msg, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
    else:
        return bot.edit_message_text(
            tg_id, msg_id, msg, parse_mode="HTML", disable_web_page_preview=True)
