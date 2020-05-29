from pyrogram import Client, Message, Filters

from handlers.filters import secret_input_filter, api_key_input_filter
from models import db, Msg


@Client.on_message(~Filters.bot & ~secret_input_filter & ~api_key_input_filter, group=-1)
def msg_monitor(bot: Client, m: Message):
    """
    Сохраняет в БД все сообщения кроме API и Secret ключей
    Полезно для анализа взаимодействия с ботом
    """
    with db.atomic():
        Msg.create(tg_id=m.from_user.id, text=m.text)


@Client.on_message(~Filters.bot)
def unknown_command(bot: Client, m: Message):
    m.delete()
