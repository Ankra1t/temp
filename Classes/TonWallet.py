from pytonconnect import TonConnect
from pytonconnect.storage import IStorage

from config_global import MANIFEST_URL
from data.data import liteDb


class TcStorage(IStorage):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id

    def _get_key(self, key: str):
        return str(self.chat_id) + key

    async def set_item(self, key: str, value: str):
        liteDb.setTonStorage(self._get_key(key), value)

    async def get_item(self, key: str, default_value: str | None = None):
        value = liteDb.getTonStorage(self._get_key(key))
        return value or default_value

    async def remove_item(self, key: str):
        liteDb.delTonStorage(self._get_key(key))


def get_connector(chat_id: int):
    return TonConnect(MANIFEST_URL, storage=TcStorage(chat_id))
