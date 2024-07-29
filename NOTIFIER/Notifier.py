from typing import Literal
from telebot import TeleBot
from telebot.types import Message
from telebot.util import antiflood
from common.dt import get_str_by_datetime

from common.lang import getLangByCode
from config_logger import logger
from db import LANGUAGES_TYPE, db
from models import SentMessages, UserInfo


MESSAGE_TYPE = Literal['text', 'photo', 'video']


class Notifier():
    def __init__(self, bot: TeleBot, bot_users: TeleBot) -> None:
        self.bot = bot
        self.bot_users = bot_users
        self.users = (156045434, 7159306363)
        self.users_info: dict[int, tuple[str, int]] = {}

    def _send_by_type(self, bot: TeleBot, user_id: int, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        mes: Message | None = None
        try:
            if type == 'photo':
                mes = antiflood(
                    bot.send_photo, user_id,
                    media_id, caption=text
                )
            elif type == 'video':
                mes = antiflood(
                    bot.send_video, user_id,
                    media_id, caption=text
                )
            else:  # text
                mes = antiflood(bot.send_message, user_id, text)
        except Exception as e:
            logger.error(f'Ошибка бота уведомлений [id = {user_id}]: {e}')

        return mes

    def _send(self, bot: TeleBot, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        chIds: list[str] = []
        mesIds: list[str] = []

        for user in self.users:
            mes = self._send_by_type(bot, user, type, text, media_id)
            if mes is not None:
                chIds.append(str(user))
                mesIds.append(str(mes.id))

        return SentMessages(
            chIds=chIds,
            mesIds=mesIds,
            langs=['ru', 'ru']
        )

    def send_notification(self, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        self._send(self.bot, type, text, media_id)

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

    def send_user_is_registered(self, userId: int, user_lang: str, num: int):
        new_user = db.get_user_by_id(userId)
        if new_user is None:
            return

        refer_user = db.get_user_by_id(new_user.refer_id or -1)

        self.users_info[userId] = (user_lang, num)

        return self._send(
            self.bot_users, 'text',
            self._get_user_mes(new_user, user_lang, num, refer_user)
        )

    def change_user_blocked(self, userId: int, sent_messages: SentMessages):
        new_user = db.get_user_by_id(userId)
        if new_user is None:
            return

        refer_user = db.get_user_by_id(new_user.refer_id or -1)

        users_info = self.users_info.get(userId)
        if users_info is None:
            return

        lang, num = users_info

        message = self._get_user_mes(new_user, lang, num, refer_user)
        message += f'\n❌ Заблокировал бота'

        for i in range(len(sent_messages.chIds)):
            try:
                self.bot_users.edit_message_text(
                    message, sent_messages.chIds[i],
                    int(sent_messages.mesIds[i]),
                )
            except:
                pass

    def change_user_choosed_lang(self, userId: int, lang: LANGUAGES_TYPE, sent_messages: SentMessages):
        new_user = db.get_user_by_id(userId)
        if new_user is None:
            return

        refer_user = db.get_user_by_id(new_user.refer_id or -1)

        users_info = self.users_info.get(userId)
        if users_info is None:
            return

        user_lang, num = users_info

        message = self._get_user_mes(new_user, lang, num, refer_user)
        message += f'\nВыбранный язык: ({getLangByCode(user_lang)})'

        for i in range(len(sent_messages.chIds)):
            try:
                self.bot_users.edit_message_text(
                    message, sent_messages.chIds[i],
                    int(sent_messages.mesIds[i]),
                )
            except:
                pass
