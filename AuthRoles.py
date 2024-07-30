from typing import Literal
import json
import requests

from db import db
from config_logger import logger
from config_global import API_URL
from common.vars import HEADERS
from models import TickerInfo


def get_site_code(user_id: int) -> str | Literal[False]:
    access_token = db.get_access_token() or ''
    user_db_id = db.get_user_id_by_tg_id(user_id)

    data: dict[str, str | int] = {
        'id': user_db_id,
    }

    try:
        response = requests.post(
            f'{API_URL}/tg/auth/site_code',
            json.dumps(data).encode(), headers=HEADERS | {'tg-api-key': access_token}
        )

        result = response.json()
        return result.get('code', False)
    except Exception as e:
        logger.error(f'/auth/get_site_code {e}')
        return False


def vote_timeout(stat_id: int):
    access_token = db.get_access_token() or ''

    try:
        res = requests.get(
            f'{API_URL}/tg/vote_timeout?stat_id={stat_id}',
            headers=HEADERS | {'tg-api-key': access_token}
        )
        print(res.json())
        return res.json()
    except Exception as e:
        logger.error(f'/auth/vote_timeout {e}')
        return False


def first_timeout(user_id: int):
    access_token = db.get_access_token() or ''

    try:
        res = requests.get(
            f'{API_URL}/tg/first_timeout?user_id={user_id}',
            headers=HEADERS | {'tg-api-key': access_token}
        )
        print(res.json())
        return res.json()
    except Exception as e:
        logger.error(f'/auth/first_timeout {e}')
        return False


def get_ticker_info(ticker: str):
    access_token = db.get_access_token() or ''

    try:
        res = requests.get(
            f'{API_URL}/tg/getTicker/{ticker.replace("/", "").upper()}',
            headers=HEADERS | {'tg-api-key': access_token}
        )
        return TickerInfo(**res.json())
    except Exception as e:
        logger.error(f'/get_ticker_info {e}')
        return False


def get_ticker_atr(ticker: str, period: str, count: int):
    access_token = db.get_access_token() or ''

    try:
        res = requests.get(
            f'{API_URL}/tg/getAvgAtr/{ticker.replace("/", "").upper()}',
            {
                'period': period,
                'count': count
            },
            headers=HEADERS | {'tg-api-key': access_token}
        )
        print(res.json())
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        logger.error(f'/get_ticker_atr {e}')
        return False


def get_ticker_delivery_fee(ticker: str):
    access_token = db.get_access_token() or ''

    try:
        res = requests.get(
            f'{API_URL}/tg/{ticker.replace("/", "").upper()}/deliveryFee',
            headers=HEADERS | {'tg-api-key': access_token}
        )
        # print(res.json())
        # if res.status_code == 200:
        #     return res.json()
    except Exception as e:
        logger.error(f'/get_ticker_delivery_fee {e}')
        return False


def change_password(id: int, password: str):
    access_token = db.get_access_token() or ''

    try:
        data = {
            'id_telegram': id,
            'password': password,
            'tg_api_auth_token': access_token
        }
        response = requests.post(
            f'{API_URL}/auth/tg_change_pass',
            json.dumps(data).encode(), headers=HEADERS
        )

        logger.info(
            f'/auth/site_code [id={id}] {response.status_code} {response.json()}'
        )
    except Exception as e:
        logger.error(
            f'/auth/site_code [id={id}] {response.status_code} {response.json()}'
        )
        return False

    return response.status_code == 200


def check_registrate(tg_id: int):
    """Возвращает роль"""
    user_db_id = db.get_user_id_by_tg_id(tg_id)
    worker_role = db.get_worker_role(user_db_id)

    if worker_role is not None:
        user_role = 1
    elif user_db_id > 0:
        user_role = 0
    else:
        user_role = None

    return user_role

# Сообщение рефералу
# if refer != 0:
#     count_ref = len(db.get_user_referals(refer))
#     self.bot.send_message(refer, text=f'<b>Поздравляем!</b>🎊\nУ Вас появился новый реферал 😎 '
#                           f'\n\n Ник: {self.nickname}\n\nУ вас рефералов: {count_ref} шт.')

# Сообщение админам
# admins = db.get_all_global_admins()
# for i in range(0, len(admins)):
#     self.bot.send_message(admins[i][0],
#                             f'Подключился новый пользователь\n ID: {self.mess.from_user.id} '
#                             f'\nUsername: {self.mess.from_user.username}')
