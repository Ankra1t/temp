from typing import Literal
import currencyapicom

from config_logger import logger

# * Response Model
# meta: {
#     last_updated_at: str
# },
# data: {
#     key: {
#         code: str
#         value: float
#     }
# }
#


class CurrencyService():
    def __init__(self, key: str) -> None:
        self.client = currencyapicom.Client(key)

    def getPrice(self, base: str, quoted: str) -> float | Literal[False]:
        try:
            response = self.client.latest(
                base.upper(), [quoted.upper()]
            )

            value = response.get('data').get(quoted).get('value')
            return value
        except Exception as e:
            logger.error(f'[get currency value]: {e}')
            return False

    def getPairsPrice(self, pairs: list[str]) -> dict[str, float] | Literal[False]:
        currencies: list[str] = []
        for pair in pairs:
            pair = pair.upper()

            pair_arr = pair.split('/')
            if len(pair_arr) != 2:
                continue

            for currency in pair_arr:
                if currency in currencies:
                    continue
                currencies.append(currency)

        try:
            response = self.client.latest(
                'USD', currencies
            )

            values: dict = response.get('data')

            prices: dict[str, float] = {}
            for el in values.keys():
                prices[el] = values.get(el, {}).get('value')

            result: dict[str, float] = {}
            for pair in pairs:
                pair = pair.upper()

                pair_arr = pair.split('/')
                if len(pair_arr) != 2:
                    continue

                result[pair] = prices[pair_arr[1]] / prices[pair_arr[0]]

            return result
        except Exception as e:
            logger.error(f'[get currencies values]: {e}')
            return False
