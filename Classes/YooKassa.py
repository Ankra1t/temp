from telebot import TeleBot
from flask import Request, Response
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import BadRequestError
import uuid

from common.utils import check_discount_price
from NOTIFIER.messages import mess_user_paid
from db import db
from Classes import pay_guard
from NOTIFIER import notifier

from common.dt import get_str_by_datetime
from messages.users import paid_subscribe_msg
from models import Price

from config_global import YOOKASSA_SECRET_KEY, YOOKASSA_SHOP_ID
from config_logger import logger

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


def yooKassa_create_payment(user_id: int, tariff: Price, redirect_url: str):
    price = check_discount_price(tariff)
    currency = tariff.currency
    name = tariff.name

    user_db_id = db.get_user_id_by_tg_id(user_id)
    if user_db_id == 0:
        return False

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
    except BadRequestError as e:
        print(e.HTTP_CODE)
        print(e)
        logger.error(f'yooKassa Error: {e}')
        return False

    url = str(payment.confirmation.confirmation_url)
    code = str(payment.id)

    db.add_transaction(
        user_db_id,
        code,
        url,
        price,
        'wait_payments',
        currency,
        name,
        tariff.duration_days,
        tariff.type_product
    )

    return url


def yooKassa_payment_updates(bot: TeleBot, request: Request):
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
        logger.error(f'Не удалось подтвердить платеж {code}')
        return Response(status=200)

    if event == 'payment.canceled':
        db.cancel_transaction(transaction.id)
        return Response(status=200)

    db.success_transaction(transaction.id)

    # Добавить платную подписку
    finish_date = pay_guard.set_paid_subscribe(transaction)
    finish_date_show = get_str_by_datetime(finish_date)

    # Обнуляем пробную подписку
    pay_guard.deactivate_user_trial_subscribe(
        transaction.user_id
    )

    # Сообщение в бот уведомлений об оплате
    summ_full = f"{transaction.sum} {transaction.currency}"

    user = db.get_user_by_id(transaction.user_id)
    if user is not None:
        bot.send_message(
            user.tg_id,
            text=paid_subscribe_msg(
                finish_date_show, transaction.name
            ),
        )
        notifier.send_notification('text', mess_user_paid(
            user_id=user.id,
            user_nike='@' + user.username if user.username else user.tg_id,
            summ_paid=summ_full,
            tariff_name=transaction.name,
            finish_date=finish_date_show
        ))

    return Response(status=200)
