from datetime import datetime, timezone
from typing import Literal
from telebot.async_telebot import AsyncTeleBot
from common.dt import get_str_by_datetime

from common.utils import antiflood
from config_logger import logger
from db import db
from models import SentMessages, UserInfo, UserNotification, LANGUAGES_TYPE
from services import user


MESSAGE_TYPE = Literal['text', 'photo', 'video']


class Notifier():
    def __init__(self, bot: AsyncTeleBot, bot_users: AsyncTeleBot, bot_site_user: AsyncTeleBot) -> None:
        self.bot = bot
        self.bot_users = bot_users
        self.bot_site_user = bot_site_user
        self.users = [7159306363]

    async def _send_by_type(self, bot: AsyncTeleBot, user_id: int, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        mes = None
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

    def _get_user_mes(self, new_user: UserInfo, num: int, lang: LANGUAGES_TYPE | None = None, block_time: datetime | None = None):
        message = f'<b>{num})</b> '
        if new_user.tg_username is not None and new_user.tg_username != '-':
            message += f'@{new_user.tg_username}'
        else:
            message += f'tg ID: <b>{new_user.tg_id}</b>'

        if lang or block_time:
            message += '\n'

        if lang:
            message += f'Язык: {lang.upper()} '
        if block_time:
            message += f'(BLOCK {get_str_by_datetime(block_time)})'

        refer_user = user.getReferralOfUser(new_user.id)

        if refer_user is not None:
            refer_name = f'@{refer_user.tgUsername}' if refer_user.tgUsername and refer_user.tgUsername != '-' else refer_user.tgId
            message += f'\nПришел от: {refer_user.id} | {refer_name} ({refer_user.refsCount})'

        return message

    async def send_user_is_registered(self, userId: int, num: int):
        new_user = db.get_user_by_id(userId)
        if new_user is None:
            return

        return await self._send(
            self.bot_users, 'text',
            self._get_user_mes(new_user, num)
        )

    async def change_user_blocked(self, userId: int, sent_messages: UserNotification):
        new_user = db.get_user_by_id(userId)
        if new_user is None:
            return

        message = self._get_user_mes(
            new_user, sent_messages.num, None, datetime.now(tz=timezone.utc)
        )

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

        message = self._get_user_mes(new_user, sent_messages.num, lang)

        for i in range(len(sent_messages.chIds)):
            try:
                await self.bot_users.edit_message_text(
                    message, sent_messages.chIds[i],
                    int(sent_messages.mesIds[i]),
                )
            except:
                pass

    async def send_site_visited(self, userId: int):
        user = db.get_user_by_id(userId)

        if not user:
            return

        name = f"@{user.tg_username}" if user.tg_username else f"id: {user.tg_id}"

        await self._send(
            self.bot_site_user, 'text',
            f"""{name} на сайте"""
        )
