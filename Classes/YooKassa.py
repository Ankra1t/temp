from flask import Request, Response
from yookassa import Configuration, Payment
import uuid

from NOTIFIER.messages import mess_user_paid
from db import db
from initialize import bot, pay_guard
from NOTIFIER import notifier

from common.dt import get_str_by_datetime
from config_global import YOOKASSA_SECRET_KEY, YOOKASSA_SHOP_ID
from messages.users import paid_subscribe_msg
from models import Transactions


Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


def create_payment(user_id: int, price: int, currency: str, name: str, redirect_url: str):
    response_data = {
        "amount": {
            "value": str(price),
            "currency": currency
        },
        "capture": True,
        "description": name
    }

    response_data["confirmation"] = {
        "type": "redirect",
        "return_url": redirect_url
    }

    try:
        payment = Payment.create(response_data, uuid.uuid4())
        if payment.confirmation is None:
            return False
    except Exception as e:
        print(f'yooKassa Error: {e}')
        return False

    url = str(payment.confirmation.confirmation_url)
    code = str(payment.id)

    db.add_transaction(Transactions(
        user_id=user_id,
        link=url,
        code=code,
        currency=currency,
        status='wait_payments',
        sum=price
    ))

    return url


def payment_updates(request: Request):
    body: dict | None = request.get_json(True, True)
    if body is None:
        return Response(status=400)

    event = body.get('event')
    payment: dict | None = body.get('object')

    success_events = ['payment.succeeded', 'payment.canceled']
    if (
        body.get('type') != 'notification'
        or (event not in success_events)
        or (type(payment) != dict)
    ):
        return Response(status=400)

    code = payment.get('id')
    if code is None:
        return Response(status=400)

    transaction = db.get_wait_transaction(code)
    if transaction is None:
        return Response(status=200)

    transaction_id = transaction.id or 0
    if event == 'payment.canceled':
        db.cancel_transaction(transaction_id)
        return Response(status=200)

    db.success_transaction(transaction_id)

    # Добавить платную подписку
    finish_date_obj = pay_guard.set_paid_subscribe(transaction)
    finish_date = get_str_by_datetime(finish_date_obj)

    tariff = db.get_price_by_id(
        transaction.price_id or 0, None
    )

    if tariff is None:
        name = '-'
    else:
        name = tariff.name

    # Обнуляем пробную подписку
    pay_guard.set_trial_subscribe_unactive_by_user(
        transaction.user_id
    )

    # Отправляем сообщение пользователю
    bot.send_message(
        transaction.user_id,
        text=paid_subscribe_msg(
            finish_date, name
        ),
    )

    # Сообщение в бот уведомлений об оплате
    summ_full = f"{transaction.sum} {transaction.currency}"
    user = db.get_user_by_tg_id(transaction.user_id)

    if user is not None:
        notifier.send_notification('text', mess_user_paid(
            user_id=user.id,
            user_nike='@' + user.username if user.username else user.tg_id,
            summ_paid=summ_full,
            tariff_name=name,
            finish_date=finish_date
        ))

    return Response(status=200)
