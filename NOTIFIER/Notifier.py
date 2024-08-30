from typing import Literal
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from common.dt import get_str_by_datetime

from common.utils import antiflood
from common.lang import getLangByCode
from config_logger import logger
from db import db
from models import SentMessages, UserInfo, UserNotification, LANGUAGES_TYPE


MESSAGE_TYPE = Literal['text', 'photo', 'video']


class Notifier():
    def __init__(self, bot: AsyncTeleBot, bot_users: AsyncTeleBot) -> None:
        self.bot = bot
        self.bot_users = bot_users
        self.users = (156045434, 7159306363)

    async def _send_by_type(self, bot: AsyncTeleBot, user_id: int, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        mes: Message | None = None
        try:
            if type == 'photo':
                mes = await antiflood(
                    bot.send_photo, user_id,
                    media_id, caption=text
                )
            elif type == 'video':
                mes = await antiflood(
                    bot.send_video, user_id,
                    media_id, caption=text
                )
            else:  # text
                mes = await antiflood(bot.send_message, user_id, text)
        except Exception as e:
            logger.error(f'Ошибка бота уведомлений [id = {user_id}]: {e}')

        return mes

    async def _send(self, bot: AsyncTeleBot, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        chIds: list[str] = []
        mesIds: list[str] = []

        for user in self.users:
            mes = await self._send_by_type(bot, user, type, text, media_id)
            if mes is not None:
                chIds.append(str(user))
                mesIds.append(str(mes.id))

        return SentMessages(
            chIds=chIds,
            mesIds=mesIds,
            langs=['ru', 'ru']
        )

    async def send_notification(self, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        await self._send(self.bot, type, text, media_id)

    def _get_user_mes(self, new_user: UserInfo, user_lang: str, num: int, refer_user: UserInfo | None = None):
        message = f'<b>{num})</b> '
        if new_user.tg_username is not None and new_user.tg_username != '-':
            message += f'@{new_user.tg_username}'
        else:
            message += f'tg ID: <b>{new_user.tg_id}</b>'

        message = f'{message} ({getLangByCode(user_lang)})'
        message += f'\n{get_str_by_datetime(new_user.registration_dt)}'

        if refer_user is not None:
            refer_name = f'@{refer_user.tg_username}' if refer_user.tg_username != '' and refer_user.tg_username != '-' else refer_user.tg_id
            message += f'\nПришел от: {refer_user.id} | {refer_name}'

        return message

    async def send_user_is_registered(self, userId: int, user_lang: str, num: int):
        new_user = db.get_user_by_id(userId)
        if new_user is None:
            return

        refer_user = db.get_user_by_id(new_user.refer_id or -1)

        return await self._send(
            self.bot_users, 'text',
            self._get_user_mes(new_user, user_lang, num, refer_user)
        )

    async def change_user_blocked(self, userId: int, sent_messages: UserNotification):
        new_user = db.get_user_by_id(userId)
        if new_user is None:
            return

        refer_user = db.get_user_by_id(new_user.refer_id or -1)

        message = self._get_user_mes(
            new_user, sent_messages.firstLang, sent_messages.num, refer_user
        )
        message += f'\n❌ Заблокировал бота'

        for i in range(len(sent_messages.chIds)):
            try:
                await self.bot_users.edit_message_text(
                    message, sent_messages.chIds[i],
                    int(sent_messages.mesIds[i]),
                )
            except:
                pass

    async def change_user_choosed_lang(self, userId: int, lang: LANGUAGES_TYPE, sent_messages: UserNotification):
        new_user = db.get_user_by_id(userId)
        if new_user is None:
            return

        refer_user = db.get_user_by_id(new_user.refer_id or -1)

        message = self._get_user_mes(new_user, sent_messages.firstLang, sent_messages.num, refer_user)
        message += f'\nВыбранный язык: ({getLangByCode(lang)})'

        for i in range(len(sent_messages.chIds)):
            try:
                await self.bot_users.edit_message_text(
                    message, sent_messages.chIds[i],
                    int(sent_messages.mesIds[i]),
                )
            except:
                pass
