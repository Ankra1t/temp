from typing import Literal
from telebot import TeleBot
from common.dt import get_str_by_datetime

from config_logger import logger
from models import UserInfo


MESSAGE_TYPE = Literal['text', 'photo', 'video']


class Notifier():
    def __init__(self, bot: TeleBot, bot_users: TeleBot) -> None:
        self.bot = bot
        self.bot_users = bot_users
        self.users = (156045434, 774944610)

    def _send_by_type(self, bot: TeleBot, user_id: int, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        try:
            if type == 'photo':
                bot.send_photo(user_id, media_id, caption=text)
            elif type == 'video':
                bot.send_video(user_id, media_id, caption=text)
            else:  # text
                bot.send_message(user_id, text)
        except Exception as e:
            logger.error(f'Ошибка бота уведомлений [id = {user_id}]: {e}')

    def _send(self, bot: TeleBot, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        for user in self.users:
            self._send_by_type(bot, user, type, text, media_id)

    def send_notification(self, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        self._send(self.bot, type, text, media_id)

    def send_user_is_registered(self, new_user: UserInfo):
        message = f'<b>Зарегистрирован новый пользователь</b>\n\n'

        if new_user.tg_username != '-':
            message += f'@{new_user.tg_username}'
        else:
            message += f'tg ID: <b>{new_user.tg_id}</b>'

        message += '\n'

        message += f'Дата и время: {get_str_by_datetime(new_user.registration_dt)}'

        self._send(self.bot_users, 'text', message)
