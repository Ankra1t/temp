from googletrans import Translator
from telebot import TeleBot

from common.utils import get_lang
from db import db


class TextEditor(object):
    """Класс редактор текстов"""

    def __init__(self, bot: TeleBot) -> None:
        self.bot = bot
        self.translator = Translator(raise_exception=True)

    def get_text(self, user_id: int, label: str):
        lang = get_lang(user_id)
        text = db.get_text_by_name(label)

        if text is not None:
            result = text.message
            if lang == 'en':
                try:
                    result = str(self.translator.translate(
                        text.message, 'en', 'ru').text)
                except:
                    result = text.message

            return result or text.message
        else:
            print('Передан несуществующий в БД label')
            return ''

    def get_media_id(self, user_id: int, label: str):
        lang = get_lang(user_id)
        text = db.get_text_by_name(label)

        if text is None:
            return ''

        if lang == 'ru':
            return text.media_id or ''
        else:
            return text.media_id_en or text.media_id or ''

    def save_content(self, name: str, content: str):
        if content:
            db.update_text(name, content)
        else:
            print('Пустой текст затрет полностью старый текст!')
