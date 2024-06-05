import requests

from data.data import liteDb


class CoinmarketService:
    def __init__(self, key: str):
        self.key = key
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.key,
        }
        self.url = 'https://pro-api.coinmarketcap.com/v1/'

    def getAllIds(self):
        res = requests.get(self.url + 'exchange/map', params={
        }, headers=self.headers)
        data = res.json()

        ids = ''
        for el in data['data']:
            ids += str(el['id']) + ','
        ids = ids[:-1]

        return ids

    def get(self):
        ids = self.getAllIds()
        res = requests.get(self.url + 'exchange/info', params={
            'id': ids,
        }, headers=self.headers)

        data = res.json()
        data = data.get('data')

        for idKey in data.keys():
            el = data.get(idKey)
            name = el.get('name')
            maker_fee = el.get('maker_fee', 0)
            taker_fee = el.get('taker_fee', 0)

            if name is not None:
                liteDb.addExchange(int(idKey), name, maker_fee, taker_fee)

