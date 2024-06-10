from pytonconnect.storage import IStorage
from data.data import liteDb

class TcStorage(IStorage):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    def _get_key(self, key: str):
        return str(self.chat_id) + key

    def set_item(self, key: str, value: str):
        liteDb.setTonStorage(self._get_key(key), value)

    def get_item(self, key: str, default_value: str | None = None):
        value = liteDb.getTonStorage(self._get_key(key))
        return value or default_value

    def remove_item(self, key: str):
        liteDb.delTonStorage(self._get_key(key))