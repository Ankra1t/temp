from telebot import types, TeleBot
from config_logger import logger

from db import db


class TextEditor(object):
    """Класс редактор текстов"""

    def __init__(self, bot: TeleBot, kb_inl_instance) -> None:
        self.bot = bot
        self.kb_inl = kb_inl_instance

    def get_text(self, label: str):
        logger.info(f'-----> Запрошен приветственный текст из БД  ')

        text = db.get_text_by_name(label)
        if text is not None:
            return text.message
        else:
            print('Передан несуществующий в БД label')
            return ''

    def save_content(self, name: str, content: str):
        if content:
            db.update_text(name, content)
        else:
            print('Пустой текст затрет полностью старый текст!')
