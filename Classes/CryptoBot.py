from httpx import request
from aiocryptopay.const import PaidButtons, InvoiceStatus

from config_global import CRYPTOPAY_TOKEN
from config_logger import logger

from common.utils import check_discount_price
from models import Price
from db import db


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
            'payload': {
                'rub_price': tariff.price
            },
            'asset': currency,
            'amount': price,
            'description': name,
            'paid_btn_name': PaidButtons.OPEN_BOT,
            'paid_btn_url': redirect_url,
            'expires_in': 1200
        }

        query = 'https://pay.crypt.bot/api/createInvoice'
        query = 'https://testnet-pay.crypt.bot/api/createInvoice'
        req = request(
            'get', query,
            params=data, headers={"Crypto-Pay-API-Token": CRYPTOPAY_TOKEN}
        )

        payment = req.json().get('result')
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
        'WAIT',
        currency,
        name,
        tariff.duration_days,
        tariff.type_product
    )

    return url
