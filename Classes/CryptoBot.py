import threading
from typing import Literal
from httpx import request
from telebot import TeleBot
import asyncio
from hashlib import sha256
from hmac import HMAC
from flask import Request, Response
from aiocryptopay import AioCryptoPay
from aiocryptopay.const import PaidButtons, InvoiceStatus

from NOTIFIER.messages import mess_user_paid
from common.dt import get_str_by_datetime
from Classes import pay_guard
from NOTIFIER import notifier

from config_global import CRYPTOPAY_TOKEN, CRYPTOPAY_NETWORK
from config_logger import logger

from common.utils import check_discount_price
from messages.users import paid_subscribe_msg
from models import Price
from db import db


# Payment = AioCryptoPay(token=CRYPTOPAY_TOKEN, network=CRYPTOPAY_NETWORK)

def cryptoPay_create_payment(user_id: int, tariff: Price, redirect_url: str):
    if tariff.price_crypto == 0:
        return False

    price = check_discount_price(tariff, 'crypto')
    currency = tariff.currency_crypto
    name = tariff.name

    user_db_id = db.get_user_id_by_tg_id(user_id)
    if user_db_id == 0:
        return False

    try:
        data = {
            'asset': currency,
            'amount': price,
            'description': name,
            'paid_btn_name': PaidButtons.OPEN_BOT,
            'paid_btn_url': redirect_url,
            'expires_in': 1200
        }
        req = request('get', 'https://pay.crypt.bot/api/createInvoice',
                          params=data, headers={"Crypto-Pay-API-Token": CRYPTOPAY_TOKEN})
        payment = req.json()
        if payment.get('status') != InvoiceStatus.ACTIVE:
            return False
    except Exception as e:
        logger.error(f'CryptoPay Error: {e}')
        return False

    url = str(payment.get('bot_invoice_url'))
    code = str(payment.get('invoice_id'))

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


def cryptoPay_payment_updates(bot: TeleBot, request: Request):
    body: dict | None = request.get_json(True, True)
    if body is None:
        return Response(status=400)

    body_text = request.get_data(True, True)
    crypto_pay_signature = request.headers.get(
        "Crypto-Pay-Api-Signature", "No value"
    )

    token = sha256(string=CRYPTOPAY_TOKEN.encode("UTF-8")).digest()
    signature = HMAC(
        key=token, msg=body_text.encode("UTF-8"), digestmod=sha256
    ).hexdigest()
    if signature != crypto_pay_signature:
        return Response(status=400)

    payment: dict | None = body.get('payload')
    if payment is None:
        return Response(status=400)

    code = str(payment.get('invoice_id'))
    if code is None:
        return Response(status=400)

    transaction = db.get_wait_transaction(code)
    if transaction is None:
        logger.error(f'Не удалось подтвердить платеж {code}')
        return Response(status=200)

    if payment.get('status', '') == 'expired':
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
                user.tg_id, finish_date_show, transaction.name
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
