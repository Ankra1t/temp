from telebot import types, TeleBot
from config_logger import logger

from db import Database


class TextEditor(object):
    """Класс редактор текстов"""

    def __init__(self, db: Database, bot: TeleBot, kb_inl_instance) -> None:
        self.db = db
        self.bot = bot
        self.kb_inl = kb_inl_instance

    def list_texts(self, chat: types.Chat):
        """Получить список текстов в админке для редактирования"""
        list = self.db.get_list_texts()
        if list:
            for i in range(0, len(list)):
                text_id = list[i][0]
                print(f'list[i] ')
                print(list[i])
                single_text = 'id={} label={} \n\n{}'.format(
                    text_id, list[i][2], list[i][3])
                self.bot.send_message(
                    chat.id, single_text,
                    reply_markup=self.kb_inl.kb_edit_single_text(text_id)
                )
        else:
            self.bot.send_message(
                chat.id, 'Тестов для редактирования не найдено'
            )

    def get_text(self, label):
        logger.info(f'-----> Запрошен приветственный текст из БД  ')

        text = self.db.get_single_text(label)
        if text:
            content = text[3]
            return content
        raise Exception('Передан несуществующий в БД label')
        # return ''

    def save_content(self, text_id, content):
        content = content.strip()
        if content:
            self.db.save_bot_text_by_id(text_id, content)
        else:
            raise Exception('Пустой текст затрет полностью старый текст!')
