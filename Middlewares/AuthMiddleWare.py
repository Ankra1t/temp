from telebot import types, TeleBot
from telebot.handler_backends import BaseMiddleware, CancelUpdate
from telebot.util import extract_arguments

from NOTIFIER import notifier

from config_logger import logger
from common.utils import delete_message, is_digit

from db import db, LANGUAGES
from AuthRoles import check_registrate, registration


class AuthMiddleWare(BaseMiddleware):
    """Класс защитник авторизации"""

    def __init__(self, bot: TeleBot, limit=2) -> None:
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message', 'edited_message']
        self.bot = bot

    def post_process(self, message: types.Message, data, exception):
        pass

    def pre_process(self, message: types.Message, data):
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username or '-'

        if self.bot.get_state(user_id, chat_id) is not None:
            with self.bot.retrieve_data(user_id, chat_id) as state_data:
                del_mes_id = state_data.get('del_mes_id')
                edit_mes = state_data.get('edit_mes')
                state_data['del_mes_id'] = None
                state_data['edit_mes'] = None

                if del_mes_id is not None:
                    if edit_mes is None:
                        delete_message(self.bot, chat_id, del_mes_id)
                    else:
                        try:
                            self.bot.edit_message_text(
                                edit_mes, message.from_user.id, del_mes_id,
                            )
                        except Exception as e:
                            pass

        data['has_registered_now'] = False

        user_db_id = db.get_user_id_by_tg_id(user_id)
        if db.check_ban_user(user_db_id):
            return CancelUpdate()

        user_role = check_registrate(user_id)

        if user_role is None:
            # Проверяем реферальный id
            ref_id = extract_arguments(message.text or '')
            ref_id = int(ref_id) if ref_id is not None and is_digit(ref_id) else None

            # Регистрация, пробный период, добавление таблиц бота
            is_registered = registration(user_id, username, ref_id)
            new_user = db.get_user_by_tg_id(user_id)

            if new_user is not None and is_registered:
                db.create_tg_user_tables(new_user.id)
                num = db.get_today_users_count()

                # Проверка языка
                user_lang = message.from_user.language_code.lower()
                lang = user_lang if (user_lang in LANGUAGES) else 'en'
                db.set_user_lang(new_user.id, lang)

                # Уведомление о регистрации
                notifier.send_user_is_registered(new_user, user_lang, num)
            else:
                logger.error(
                    f'Ошибка регистрации пользователя tg_id = {user_id} {username}'
                )

            data['has_registered_now'] = True
            user_role = 0
        else:
            # Если нет таблицы связанной с ботом, то создаем
            is_tg_tables = db.check_tg_user_tables(user_db_id)
            if not is_tg_tables:
                db.create_tg_user_tables(user_db_id)

        data['user_role'] = user_role

        # Защита от флуда отключена
        # if message.from_user.id not in self.last_time:
        #   User is not in a dict, so lets add and cancel this function
        # self.last_time[message.from_user.id] = message.date
        # return
        # if message.date - self.last_time[message.from_user.id] < self.limit:
        #     User is flooding
        # self.bot.send_message(message.chat.id, 'You are making request too often')
        # logger.info(f'Пользователь флудит (быстро отправляет одни и те же сообщения) message.from_user.id')
        #
        # return CancelUpdate()
        # self.last_time[message.from_user.id] = message.date

        # return SkipHandler() -> this will skip handler
        # return CancelUpdate() -> this will cancel update
