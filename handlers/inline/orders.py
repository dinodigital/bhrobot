import time
from pprint import pprint

from pyrogram import Client, CallbackQuery, Filters

from _interface.inline_markups import full_order_create_btns, cancel_order_btn, \
    refresh_order_btn, refresh_main_btn
from _interface.messages import gen_err_msg, gen_main_msg, err_creds, input_api_key_msg, err
from handlers.filters import hide_filter
from helpers.bithumb import bh_publish_order, get_balance
from helpers.bithumb_api import BithumbGlobalRestAPI
from helpers.db import db_save, create_order
from helpers.orders import parse_full_order_data, refresh_order_msg
from helpers.telegram import edit_message
from models import User, Order


@Client.on_callback_query(~Filters.bot & Filters.callback_data('delete_order'))
def delete_order(bot: Client, q: CallbackQuery):
    tg_id = q.from_user.id
    user = User.get(tg_id=tg_id)

    edit_message(bot, tg_id, user.temp['msg_ids'][1], '🕐 Deleting order')
    time.sleep(1)
    bot.delete_messages(tg_id, user.temp['msg_ids'])


@Client.on_callback_query(~Filters.bot & Filters.callback_data('publish_order'))
def publish_order(bot: Client, q: CallbackQuery):
    tg_id = q.from_user.id
    user = User.get(tg_id=tg_id)
    order_msg_id = user.temp['msg_ids'][1]  # 0 - user, 1 - bot
    text = user.temp['text']
    params = parse_full_order_data(text)
    pprint(params)

    # Уведомляем о публикации ордера на БХ
    bot.edit_message_text(tg_id, order_msg_id, '🕐 Publishing order...')

    # Размещаем ордер
    bh = BithumbGlobalRestAPI(user.api_key, user.secret)

    try:
        order_id = bh_publish_order(bh, params)
        if type(order_id) is tuple:
            err_msg = order_id[1]
            edit_message(bot, user.tg_id, order_msg_id, gen_err_msg(
                f'🔴 <b>Error</b>\n{err_msg}\n\nPlease, create new order'))
            return
    except Exception as e:
        err_msg = e.msg
        edit_message(bot, user.tg_id, order_msg_id, gen_err_msg(f'🔴 <b>Error</b>\n{err_msg}\n\nTry again'),
                     reply_markup=full_order_create_btns())
        return

    # Создаем ордер в БД
    order = create_order(order_id, text, params, user, status='active')
    print(f'Order #{order.id} created. Order_id: {order_id}')

    # Обновляем сообщение
    try:
        refresh_order_msg(order, bh, bot, user)
        user.temp = {}
        user.orders_count += 1
        db_save(user)
    except Exception as e:
        err_msg = e.msg
        edit_message(bot, user.tg_id, order_msg_id, gen_err_msg(f'🔴 <b>Error</b>\n{err_msg}\n\nTry again'),
                     reply_markup=refresh_order_btn())

    return


@Client.on_callback_query(~Filters.bot & Filters.callback_data('refresh_order'))
def refresh_order(bot: Client, q: CallbackQuery):
    tg_id = q.from_user.id
    user = User.get(tg_id=tg_id)
    order_msg_id = q.message.message_id
    order = Order.get(b_msg_id=order_msg_id)
    bh = BithumbGlobalRestAPI(user.api_key, user.secret)

    edit_message(bot, tg_id, order_msg_id, '🕐 Refreshing data...')

    # Обновляем сообщение
    try:
        refresh_order_msg(order, bh, bot, user)
    except Exception as e:
        err_msg = e.msg
        edit_message(bot, user.tg_id, order_msg_id, gen_err_msg(f'🔴 <b>Error</b>\n{err_msg}\n\nTry again'),
                     reply_markup=refresh_order_btn())


@Client.on_callback_query(~Filters.bot & Filters.callback_data('cancel_active_order'))
def cancel_order(bot: Client, q: CallbackQuery):
    tg_id = q.from_user.id
    user = User.get(tg_id=tg_id)
    msg_id = q.message.message_id
    order = Order.get(b_msg_id=msg_id)
    u_msg_id = order.u_msg_id

    bh = BithumbGlobalRestAPI(user.api_key, user.secret)

    bot.edit_message_text(tg_id, msg_id, '🕐 Cancelling order...')

    try:
        bh.cancel_order(order.pair, order.order_id)
        order.status = 'cancelled'
        user.orders_count -= 1
        db_save(order)
        db_save(user)
        print(f'Order {order.order_id} cancelled')

        bot.edit_message_text(tg_id, msg_id, '✅ Order cancelled...')
        time.sleep(2)
        bot.delete_messages(tg_id, [msg_id, u_msg_id])

    except Exception as e:
        if e.code == '20012':
            # Статус ордера изменился
            bh_response = bh.post('singleOrder', {
                'orderId': order.order_id,
                'symbol': order.pair})
            if bh_response['status'] == 'cancel':
                order.status = 'cancelled'
                db_save(order)
                print(f'Order {order.order_id} cancelled')

                bot.edit_message_text(tg_id, msg_id, '⚠️ Order was already cancelled on Exchange...')
                time.sleep(2)
                bot.delete_messages(tg_id, [msg_id, u_msg_id])
                return

        err_msg = e.msg
        edit_message(bot, user.tg_id, msg_id, gen_err_msg(f'🔴 <b>Error</b>\n{err_msg}\n\nTry again'),
                     reply_markup=cancel_order_btn())


@Client.on_callback_query(~Filters.bot & Filters.callback_data('refresh_main'))
def rfrsh_main(bot: Client, q: CallbackQuery):
    tg_id = q.from_user.id
    msg_id = q.message.message_id
    user = User.get_or_none(tg_id=tg_id)

    edit_message(bot, user.tg_id, msg_id, '🕐 Refreshing data...')

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


@Client.on_callback_query(~Filters.bot & hide_filter)
def hide(bot: Client, q: CallbackQuery):
    data = q.data.split('_')

    q.message.delete()

    print(data)
    if len(data) == 2:
        msg_id = int(data[1])
        bot.delete_messages(q.message.from_user.id, [msg_id])
