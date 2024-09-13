from typing import Literal
from googletrans import Translator

from config_logger import logger
from db import db


class TextEditor(object):
    """Класс редактор текстов"""

    def __init__(self) -> None:
        self.translator = Translator(raise_exception=True)

    def get(self, label: str, lang: Literal['ru', 'en'] = 'ru') -> tuple[str | None, str | None]:
        """
            Returns:
                message, media_id
        """
        text = db.get_text_by_name(label)

        if not text:
            logger.warning(f'Передан несуществующий в БД label -> {label}')
            return (None, None)

        return (
            text.message if lang == 'ru' else None,
            text.media_id if lang == 'ru' else text.media_id_en or text.media_id
        )
