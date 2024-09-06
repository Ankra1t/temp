from typing import Union
from telebot.types import Message, CallbackQuery
from telebot.async_telebot import AsyncTeleBot, BaseMiddleware, CancelUpdate
from telebot.util import update_types

from AuthRoles import check_registrate
from common.utils import delete_message, get_lang

from db import db
from models import User, StateContext


class AuthMiddleWare(BaseMiddleware):
    """Класс защитник авторизации"""

    def __init__(self, bot: AsyncTeleBot) -> None:
        self.update_sensitive = False
        self.update_types = update_types
        self.bot = bot

    async def post_process(self, message, data, exception):
        pass

    async def pre_process(self, message: Union[Message, CallbackQuery], data):
        if message.from_user is None:
            return CancelUpdate()

        tgId = message.from_user.id
        user_db_id = db.get_user_id_by_tg_id(tgId)
        if db.check_ban_user(user_db_id):
            return CancelUpdate()

        isText = False
        if isinstance(message, Message):
            chat_id = message.chat.id
            isText = message.content_type == 'text'
        else:
            chat_id = message.message.chat.id


        state = StateContext(message, self.bot)  # type: ignore

        if (await state.get() is not None) and isText:
            async with state.data() as state_data:
                del_mes_id = state_data.get('del_mes_id')
                edit_mes = state_data.get('edit_mes')

            await self.bot.add_data(
                tgId, chat_id,
                del_mes_id=None,
                edit_mes=None
            )

            if del_mes_id is not None:
                if edit_mes is None:
                    await delete_message(self.bot, chat_id, del_mes_id)
                else:
                    try:
                        await self.bot.edit_message_text(
                            edit_mes, tgId, del_mes_id,
                        )
                    except Exception as e:
                        pass

        lang = get_lang(tgId)

        data["state"] = state
        data["user"] = User(
            id=user_db_id,
            tgId=tgId,
            lang=lang,
            role=check_registrate(tgId) or 0
        )
