from telebot import types, TeleBot
from telebot.handler_backends import BaseMiddleware, CancelUpdate

from common.utils import delete_message

from db import db
from AuthRoles import check_registrate


class AuthMiddleWare(BaseMiddleware):
    """Класс защитник авторизации"""

    def __init__(self, bot: TeleBot) -> None:
        self.update_types = ['message', 'edited_message']
        self.bot = bot

    def post_process(self, message: types.Message, data, exception):
        pass

    def pre_process(self, message: types.Message, data):
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username

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


