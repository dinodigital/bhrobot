from pyrogram import Client, Message, Filters


@Client.on_message(~Filters.bot)
def unknown_command(bot: Client, m: Message):
    m.delete()
