from typing import Literal
from telebot import TeleBot
from common.dt import get_str_by_datetime

from models import UserInfo


MESSAGE_TYPE = Literal['text', 'photo', 'video']


class Notifier():
    def __init__(self, bot: TeleBot) -> None:
        self.bot = bot
        self.users = (156045434, 396355273, 774944610)

    def _send_by_type(self, type: MESSAGE_TYPE, user_id: int, text: str, media_id: str | None = None):
        try:
            if type == 'photo':
                self.bot.send_photo(user_id, media_id, caption=text)
            elif type == 'video':
                self.bot.send_video(user_id, media_id, caption=text)
            elif type == 'text':
                self.bot.send_message(user_id, text)
        except Exception as e:
            print(f'Ошибка бота уведомлений: {e}')

    def send_notification(self, type: MESSAGE_TYPE, text: str, media_id: str | None = None):
        for user in self.users:
            self._send_by_type(type, user, text, media_id)

    def send_user_is_registered(self, new_user: UserInfo):
        message = f'<b>Зарегистрирован новый пользователь</b>\n\n'
        if new_user.username != '':
            message += f'@{new_user.username}\n'
        message += f'Дата и время: {get_str_by_datetime(new_user.registration_dt)}'

        self.send_notification('text', message)
