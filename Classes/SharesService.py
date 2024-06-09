
import requests


class SharesService(object):
    def __init__(self) -> None:
        self.url = 'https://finnhub.io/api/v1/'

    def check(self, name: str):
        res = requests.get(
            f'{self.url}/search?q={name}&token={"cpirg6pr01qlu187103gcpirg6pr01qlu1871040"}'
        )

        data = res.json()
        if data.get('count') == 0:
            return False

        for el in data.get('result', []):
            if (
                name in el.get('description') or
                name in el.get('displaySymbol') or
                name in el.get('symbol')
            ):
                return True

        return False
