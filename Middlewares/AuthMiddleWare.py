from typing import Union
from telebot.types import Message, CallbackQuery, ChatMemberUpdated
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import (
    BaseMiddleware,
    CancelUpdate,
    ContinueHandling,
)
from telebot.util import update_types

from common.utils import delete_message, get_lang
from service.auth import register_user_from_tg

from models import User, StateContext


class AuthMiddleWare(BaseMiddleware):
    """Класс защитник авторизации"""

    def __init__(self, bot: AsyncTeleBot) -> None:
        self.update_sensitive = False
        self.update_types = update_types
        self.bot = bot

    async def post_process(self, message, data, exception):
        pass

    async def pre_process(
        self, message: Union[Message, CallbackQuery, ChatMemberUpdated], data
    ):
        if isinstance(message, ChatMemberUpdated):
            return ContinueHandling()

        if message.from_user is None:
            return CancelUpdate()

        tgId = message.from_user.id
        user = await register_user_from_tg(tgId)

        isText = False
        if isinstance(message, Message):
            chat_id = message.chat.id
            isText = message.content_type == "text" or message.content_type == "photo"
        else:
            if message.message is None:
                return CancelUpdate()
            chat_id = message.message.chat.id

        state = StateContext(message, self.bot)  # type: ignore

        if (await state.get() is not None) and isText:
            async with state.data() as state_data:
                del_mes_id = state_data.get("del_mes_id")
                edit_mes = state_data.get("edit_mes")

            await state.add_data(del_mes_id=None, edit_mes=None)

            if del_mes_id is not None:
                if edit_mes is None:
                    await delete_message(self.bot, chat_id, del_mes_id)
                else:
                    try:
                        await self.bot.edit_message_text(
                            edit_mes,
                            tgId,
                            del_mes_id,
                        )
                    except Exception as e:
                        pass

        lang = get_lang()

        data["state"] = state
        data["user"] = User(id=0, tgId=tgId, lang=lang, role=0)
