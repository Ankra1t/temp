from telebot import types, TeleBot
from config_logger import logger

from db_new import db_new


class TextEditor(object):
    """Класс редактор текстов"""

    def __init__(self, bot: TeleBot, kb_inl_instance) -> None:
        self.bot = bot
        self.kb_inl = kb_inl_instance

    def list_texts(self, chat: types.Chat):
        """Получить список текстов в админке для редактирования"""
        list = db_new.get_texts()
        if len(list) != 0:
            for i in range(0, len(list)):
                text = list[i]

                text_show = f'ID: <b>{text.id}</b> | <b>{text.name}</b>\n\n{text.message}'

                self.bot.send_message(
                    chat.id, text_show,
                    reply_markup=self.kb_inl.kb_edit_single_text(text.name)
                )
        else:
            self.bot.send_message(
                chat.id, 'Текстов для редактирования не найдено'
            )

    def get_text(self, label: str):
        logger.info(f'-----> Запрошен приветственный текст из БД  ')

        text = db_new.get_text_by_name(label)
        if text is not None:
            return text.message
        else:
            print('Передан несуществующий в БД label')
            return ''

    def save_content(self, name: str, content: str):
        if content:
            db_new.update_text(name, content)
        else:
            print('Пустой текст затрет полностью старый текст!')
