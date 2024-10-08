import requests

from db import db
from config_logger import logger
from config_global import API_URL
from common.vars import HEADERS


def vote_timeout(stat_id: int):
    access_token = db.get_access_token() or ''

    try:
        res = requests.get(
            f'{API_URL}/tg/vote_timeout?stat_id={stat_id}',
            headers=HEADERS | {'tg-api-key': access_token}
        )
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
        return res.json()
    except Exception as e:
        logger.error(f'/auth/first_timeout {e}')
        return False


def check_registration(tg_id: int):
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
