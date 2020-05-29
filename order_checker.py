from datetime import datetime
from pprint import pprint

from pyrogram import Client

from _interface.inline_markups import hide_message_btn
from _interface.messages import completed_order_msg, cancelled_order_msg
from config import get_cfg
from helpers.bithumb_api import BithumbGlobalRestAPI
from helpers.db import db_save
from helpers.telegram import send_message, edit_message
from models import Order, User

from threading import Thread
import time


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def get_order(order):
    return bh.post('singleOrder', {
        'orderId': order.order_id,
        'symbol': order.pair})


def multi_request(orders, latency=0.11):
    """
    Многопоточный обработчик запросов
    На входе список url адресов
    На выходе список request объектов
    """
    threads = []
    for order in orders:
        threads.append(ThreadWithReturnValue(target=get_order, args=(order, )))

    results = []

    for thread in threads:
        thread.start()
        time.sleep(latency)

    for thread in threads:
        results.append(thread.join())

    return results


cfg = get_cfg('bithumb_info')
bh = BithumbGlobalRestAPI(cfg['key'], cfg['secret'])


def check_orders():
    orders = Order.select().where(Order.status == 'active')

    if len(orders) == 0:
        return

    r = multi_request(orders)

    success = []
    cancel = []
    for i, order in enumerate(orders, 0):
        bh_status = r[i]['status']

        if bh_status == 'success':
            success.append(order)
        elif bh_status == 'cancel':
            cancel.append(order)

    if not success and not cancel:
        return

    bot = Client('Listener', no_updates=True)
    bot.start()

    if success:
        for order in success:
            # Уведомление о выполнении ордера
            msg = '<b>Order completed</b>'
            bot.send_message(order.tg_id, msg, reply_to_message_id=order.b_msg_id, reply_markup=hide_message_btn())

            # Меняем сообщение с одрером
            order_msg = completed_order_msg(order)
            edit_message(bot, order.tg_id, order.b_msg_id, order_msg, reply_markup=hide_message_btn(order.u_msg_id))

            user = User.get(tg_id=order.tg_id)
            user.orders_count -= 1
            order.status = 'success'
            db_save(order)
            db_save(user)

    if cancel:
        for order in cancel:
            # Меняем сообщение с одрером
            order_msg = cancelled_order_msg(order.text)
            edit_message(bot, order.tg_id, order.b_msg_id, order_msg, reply_markup=hide_message_btn(order.u_msg_id))

            user = User.get(tg_id=order.tg_id)
            user.orders_count -= 1
            order.status = 'cancel'
            db_save(order)
            db_save(user)

    bot.stop()


while True:
    try:
        print(f'{datetime.now()} > Checking orders')
        check_orders()
        time.sleep(10)
    except Exception as e:
        print(f'Error: {e}')