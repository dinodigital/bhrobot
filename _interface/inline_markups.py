from pyrogram import InlineKeyboardMarkup, InlineKeyboardButton


def language_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton(text='🇬🇧 English', callback_data='lang_en')],
                                 [InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang_ru')]])


def resend_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton(text='🔄 Изменить API ключ', callback_data='resend_creds')]])


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Купить', callback_data='buy'), InlineKeyboardButton(text='Продать', callback_data='sell')]
    ])


def full_order_create_btns():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='🚀 Publish order', callback_data='publish_order')],
        [InlineKeyboardButton(text='🚫️ Delete', callback_data='delete_order')]
    ])


def full_order_active_btns():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='🔄 Refresh', callback_data='refresh_order')],
        [InlineKeyboardButton(text='🚫️ Cancel order', callback_data='cancel_active_order')]
    ])


def cancel_order_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='🚫️ Cancel order', callback_data='cancel_active_order')]
    ])


def refresh_order_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='🔄 Refresh', callback_data='refresh_order')]
    ])


def refresh_main_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='🔄 Refresh', callback_data='refresh_main')],
        [InlineKeyboardButton(text='ℹ️ How to use bot', url='https://teletype.in/@bithumbrobot/0e4FVMPme')]
    ])


def hide_message_btn(msg_id=None):
    if msg_id is None:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text='>> Hide <<', callback_data=f'hide')]])

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text='>> Hide <<', callback_data=f'hide_{msg_id}')]])