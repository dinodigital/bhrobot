from pyrogram import Message

from helpers.telegram import handle_username
from models import db, User, Order


def create_user(message: Message):
    """
    Создаем нового юзера в базе данных
    """
    tg_id = message.from_user.id
    username = handle_username(message)

    with db.atomic():
        user = User.create(
            tg_id=tg_id,
            username=username
        )

    return user


def create_order(order_id, text, params, user, status):

    with db.atomic():
        order = Order.create(
            order_id=order_id,
            tg_id=user.tg_id,
            text=text,
            side=params['side'],
            pair=params['symbol'],
            price=str(params['price']),
            quantity=str(params['quantity']),
            type=params['type'],
            b_msg_id=user.temp['msg_ids'][1],
            u_msg_id=user.temp['msg_ids'][0],
            status=status
        )

    return order


def db_save(model):
    """
    Атомарная транзакция сохранения в базе данных
    """
    with db.atomic():
        model.save()
