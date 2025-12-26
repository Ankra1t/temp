import traceback
from yookassa import Configuration, Payment
from requests.exceptions import HTTPError
import uuid

from common.utils import check_discount_price
from db import db

from models import Price

from config_global import YOOKASSA_SECRET_KEY, YOOKASSA_SHOP_ID
from config_logger import logger

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


def yooKassa_create_payment(user_id: int, tariff: Price, redirect_url: str, user_email=''):
    price = check_discount_price(tariff)
    currency = tariff.currency
    name = tariff.name

    user_db_id = db.get_user_id_by_tg_id(user_id)
    if user_db_id == 0:
        return False

    response_data = {
        "amount": {
            "value": f"{price:.2f}",
            "currency": currency
        },
        "capture": True,
        "description": name,
        "confirmation": {
            "type": "redirect",
            "return_url": redirect_url
        },
        "receipt": {
            "customer": {
                "email": user_email or 'admin@profmarkets.ai'
            },
            "items": [{
                "description": name,
                "amount": {
                    'value': f"{price / tariff.duration_days:.2f}",
                    'currency': currency
                },
                "quantity": str(tariff.duration_days),
                "measure": "day",
                "vat_code": 1,
                "payment_mode": "full_payment"
            }],
            "tax_system_code": 2
        }
    }

    try:
        payment = Payment.create(response_data, uuid.uuid4())
        if payment.confirmation is None:
            return False
    except HTTPError as e:
        return False
    except Exception as e:
        traceback.print_exc()
        logger.error(f'yooKassa Error: {e}')
        return False

    url = str(payment.confirmation.confirmation_url)
    code = str(payment.id)

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
