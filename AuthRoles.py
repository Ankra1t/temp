from typing import Literal
import json
import requests

from db import db
from config_logger import logger
from config_global import API_URL
from common.vars import HEADERS


def registration(user_id: int, username: str = '', referral_id: int = 0):
    access_token = db.get_access_token() or ''

    data: dict[str, str | int] = {
        'id_telegram': user_id,
        'tg_api_auth_token': access_token,
        'username_tg': username
    }

    try:
        response = requests.post(
            f'{API_URL}/auth/tg_register',
            json.dumps(data).encode(), headers=HEADERS
        )

        logger.info(
            f'/auth/tg_register [id={user_id}, username={username}] {response.status_code} {response.json()}'
        )
    except Exception as e:
        logger.error(f'/auth/tg_register {e}')

        return False

    return response.status_code >= 200 and response.status_code < 300


def get_site_code(user_id: int) -> str | Literal[False]:
    access_token = db.get_access_token() or ''
    user_db_id = db.get_user_id_by_tg_id(user_id)

    data: dict[str, str | int] = {
        'user_id': user_db_id,
        'tg_api_auth_token': access_token,
    }

    try:
        response = requests.post(
            f'{API_URL}/auth/site_code',
            json.dumps(data).encode(), headers=HEADERS
        )

        result = response.json()
        return result.get('code', False)
    except:
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
        user_role = worker_role
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
