from telebot import types
from telebot.handler_backends import BaseMiddleware, CancelUpdate
from NOTIFIER import notifier


from db import db, LANGUAGES
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

        user_db_id = db.get_user_id_by_tg_id(user_id)
        if db.check_ban_user(user_db_id):
            return CancelUpdate()

        user_role = check_registrate(user_id)

        if user_role is None:
            # Проверяем реферальный id
            ref_id = message.text
            ref_id = ref_id.split() if (ref_id is not None) else []

            if len(ref_id) == 2 and ref_id[0] == '/start' and ref_id[1].isdigit():
                ref_id = int(ref_id[1])
            else:
                ref_id = 0

            # Регистрация, пробный период, добавление таблиц бота
            is_registered = registration(user_id, username, ref_id)
            new_user = db.get_user_by_tg_id(user_id)

            if new_user is not None and is_registered:
                db.create_tg_user_tables(new_user.id)

                # Проверка языка
                lang = message.from_user.language_code.lower()
                lang = lang if (lang in LANGUAGES) else 'en'
                db.set_user_lang(new_user.id, lang)

                # Уведомление о регистрации
                notifier.send_user_is_registered(new_user)

                # Назначение тестовой подписки новому пользователю
                # pay_guard.set_trial(user_id)
                # Запланировать сообщение о пробной подписке через час
                # date_1hour =  datetime.now() + timedelta(hours=1)
                # serv_tasks.plan_message(user_id, date_1hour, welcome_trial_subscribe_msg(pay_guard.get_option_trial_days()))

                # notifier.send_notification('text', mess_set_trial_subsctibe_new_user(
                #     user_id=new_user.id,
                #     user_nike=f'@{new_user.username}' if new_user.username else str(new_user.tg_id),
                #     days=pay_guard.get_option_trial_days()
                # ))
            else:
                print(f'Ошибка регистрации пользователя tg_id = {user_id} {username}')

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

    def post_process(self, message, data, exception):
        pass
