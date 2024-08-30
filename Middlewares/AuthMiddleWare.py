from telebot.async_telebot import types, AsyncTeleBot, BaseMiddleware, CancelUpdate

from common.utils import delete_message

from db import db


class AuthMiddleWare(BaseMiddleware):
    """Класс защитник авторизации"""

    def __init__(self, bot: AsyncTeleBot) -> None:
        self.update_types = ['message', 'edited_message']
        self.bot = bot

    async def post_process(self, message: types.Message, data, exception):
        pass

    async def pre_process(self, message: types.Message, data):
        user_id = message.from_user.id
        chat_id = message.chat.id
        username = message.from_user.username

        if await self.bot.get_state(user_id, chat_id) is not None:
            async with self.bot.retrieve_data(user_id, chat_id) as state_data:
                del_mes_id = state_data.get('del_mes_id')
                edit_mes = state_data.get('edit_mes')
                state_data['del_mes_id'] = None
                state_data['edit_mes'] = None
                if del_mes_id is not None:
                    if edit_mes is None:
                        await delete_message(self.bot, chat_id, del_mes_id)
                    else:
                        try:
                            await self.bot.edit_message_text(
                                edit_mes, message.from_user.id, del_mes_id,
                            )
                        except Exception as e:
                            pass

        user_db_id = db.get_user_id_by_tg_id(user_id)
        if db.check_ban_user(user_db_id):
            return CancelUpdate()


