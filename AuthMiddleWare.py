from telebot import types
from telebot.handler_backends import BaseMiddleware
from telebot.handler_backends import CancelUpdate
from NOTIFIER import notifier

from initialize import pay_guard
from db_new import db_new, LANGUAGES
from GuardPaymentAccess import GuardPaymentAccess
from AuthRoles import check_registrate, registration


class AuthMiddleWare(BaseMiddleware):
    """Класс защитник авторизации"""

    def __init__(self, bot, limit=2) -> None:
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message', 'edited_message']
        self.bot = bot

    def pre_process(self, message: types.Message, data):
        user_id = message.from_user.id
        username = message.from_user.username

        data['has_registered_now'] = False

        user_db_id = db_new.get_user_id_by_tg_id(user_id)
        if db_new.check_ban_user(user_db_id):
            return CancelUpdate()

        user_role = check_registrate(user_id)
        print(f'---------------user_role -----------------')
        print(user_role)
        if user_role is None:
            # Проверяем реферальный id
            ref_id = message.text
            ref_id = ref_id.split() if (ref_id is not None) else []

            if len(ref_id) == 2 and ref_id[0] == '/start' and ref_id[1].isdigit():
                ref_id = int(ref_id[1])
            else:
                ref_id = 0

            # Регистрация, пробный период, доавбление таблиц бота
            registration(user_id, username, ref_id)
            new_user = db_new.get_user_by_tg_id(user_id)

            pay_guard.set_trial(message)

            if new_user is not None:
                db_new.create_tg_user_tables(new_user.id)

                # Проверка языка
                lang = message.from_user.language_code.lower()
                lang = lang if (lang in LANGUAGES) else 'ru'
                db_new.set_user_lang(new_user.id, lang)

                # Уведомление о регистрации
                notifier.send_user_is_registered(new_user)
            else:
                print(f'Ошибка регистрации пользователя tg_id = {user_id}')

            data['has_registered_now'] = True
            user_role = 0

        # Если нет таблицы связаной с ботом, то создаем
        is_tg_tables = db_new.check_tg_user_tables(user_db_id)
        if not is_tg_tables and user_role == 0:
            db_new.create_tg_user_tables(user_db_id)

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

    def post_process(self, message, data, exception):
        pass
