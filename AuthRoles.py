import json
import requests

from db import db
from db_new import db_new
from common.vars import API_URL, HEADERS


def registration(user_id: int, username: str = '', referral_id: int = 0):
    access_token = db_new.get_access_token() or ''

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

        print(response.status_code)
        print(response.json())
    except:
        return False

    return response.status_code == 200


def change_password(id: int, password: str):
    access_token = db_new.get_access_token() or ''

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

        print(response.status_code)
        print(response.json())
    except Exception as e:
        print(e)
        return False

    return response.status_code == 200


def check_registrate(tg_id: int):
    """Возвращает роль"""
    check_user = db_new.get_user_id_by_tg_id(tg_id)
    check_worker = db.check_worker(tg_id)
    user_role = None

    if check_worker:
        user_role = db.get_role(tg_id)
    elif check_user != 0:
        user_role = 0

    return user_role

# Сообщение рефералу
# if refer != 0:
#     count_ref = len(db_new.get_user_referals(refer))
#     self.bot.send_message(refer, text=f'<b>Поздравляем!</b>🎊\nУ Вас появился новый реферал 😎 '
#                           f'\n\n Ник: {self.nickname}\n\nУ вас рефералов: {count_ref} шт.')

# Сообщение админам
# admins = self.db.get_all_global_admins()
# for i in range(0, len(admins)):
#     self.bot.send_message(admins[i][0],
#                             f'Подключился новый пользователь\n ID: {self.mess.from_user.id} '
#                             f'\nUsername: {self.mess.from_user.username}')
