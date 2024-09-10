import requests
from data.data import liteDb

from config_logger import logger
from time import sleep
from selenium import webdriver as wd
from selenium.webdriver.common.by import By


class CoinmarketService:
    def __init__(self, key: str):
        self.key = key
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.key,
        }
        self.url = 'https://pro-api.coinmarketcap.com/v1/'

    def findByBit(self):
        browser = wd.Chrome()
        browser.maximize_window()

        browser.get('https://www.bybit.com/en/my-fee-rate/all-fee-rate/')
        sleep(2)

        table = browser.find_element(By.CLASS_NAME, 'ant-table-tbody')
        if table is None:
            return

        result: list[tuple[str, float, float]] = []

        for tr in table.find_elements(By.TAG_NAME, 'tr'):
            try:
                if tr.get_attribute('aria-hidden') is not None:
                    continue

                td = tr.find_elements(By.TAG_NAME, 'td')
                if len(td) < 5:
                    continue

                name = td[0].get_attribute('textContent')
                maker = td[2].get_attribute('textContent')
                taker = td[1].get_attribute('textContent')
                if name is None or maker is None or taker is None:
                    continue

                result.append((name, float(maker), float(taker)))
            except Exception as e:
                # logger.error(f'ERROR {[el.text for el in td]} {e}')
                pass

        browser.close()
        return result

    def findBinance(self):
        browser = wd.Chrome()
        browser.maximize_window()

        browser.get('https://www.binance.com/en/fee/trading')
        sleep(2)

        table = browser.find_element(By.CLASS_NAME, 'bn-web-table-tbody')
        if table is None:
            return

        result: list[tuple[str, float, float]] = []

        for tr in table.find_elements(By.TAG_NAME, 'tr'):
            try:
                if tr.get_attribute('aria-hidden') is not None:
                    continue

                td = tr.find_elements(By.TAG_NAME, 'td')
                if len(td) < 5:
                    continue

                name = td[0].get_attribute('textContent')
                value = td[4].get_attribute('textContent')
                if name is None or value is None:
                    continue

                maker, taker = value.replace(
                    '%', '').replace(' ', '').split('/')
                result.append((name, float(maker), float(taker)))
            except Exception as e:
                # logger.error(f'ERROR {[el.text for el in td]} {e}')
                pass

        browser.close()
        return result

    def findKucoin(self):
        browser = wd.Chrome()
        browser.maximize_window()

        browser.get('https://www.kucoin.com/ru/vip/privilege')
        sleep(2)

        table = browser.find_element(By.TAG_NAME, 'table')

        if table is None:
            return

        result: list[tuple[str, float, float]] = []

        for tr in table.find_elements(By.TAG_NAME, 'tr'):
            try:
                if tr.get_attribute('aria-hidden') is not None:
                    continue

                td = tr.find_elements(By.TAG_NAME, 'td')
                if len(td) < 7:
                    continue

                name = td[0].get_attribute('textContent')
                value = td[6].get_attribute('textContent')
                if name is None or value is None:
                    continue

                maker, taker = (
                    value
                    .replace('%', '').replace(' ', '')
                    .replace('\xa0', '').replace(',', '.').split('/')
                )
                result.append((name, float(maker), float(taker)))
            except Exception as e:
                # logger.error(f'ERROR {[el.text for el in td]} {e}')
                pass

        browser.close()
        return result

    def findOkx(self):
        browser = wd.Chrome()
        browser.maximize_window()

        browser.get('https://www.okx.com/ru/fees')
        sleep(2)

        tables = browser.find_elements(By.CLASS_NAME, 'fee-level-table')

        if tables is None:
            return

        result: list[tuple[str, float, float]] = []

        for num, table in enumerate(tables):
            left_col = table.find_element(
                By.CLASS_NAME, 'left-content').find_elements(By.XPATH, '*')
            right_col = table.find_elements(By.CLASS_NAME, 'right-column')

            maker = right_col[2 - num].find_elements(By.XPATH, '*')
            taker = right_col[3 - num].find_elements(By.XPATH, '*')

            for i in range(1, len(left_col)):
                try:
                    name = left_col[i].get_attribute('textContent')
                    maker_fee = maker[i].get_attribute('textContent')
                    taker_fee = taker[i].get_attribute('textContent')

                    if name is None or maker_fee is None or taker_fee is None:
                        continue

                    maker_fee = (
                        maker_fee
                        .replace('%', '').replace(' ', '')
                        .replace('\xa0', '').replace(',', '.')
                    )

                    taker_fee = (
                        taker_fee
                        .replace('%', '').replace(' ', '')
                        .replace('\xa0', '').replace(',', '.')
                    )

                    result.append((name, float(maker_fee), float(taker_fee)))
                except Exception as e:
                    # logger.error(f'ERROR {name} {maker_fee} {taker_fee} {e}')
                    pass

        browser.close()
        return result

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
        logger.info('GET exhanges STARTED')
        ids = self.getAllIds()
        res = requests.get(self.url + 'exchange/info', params={
            'id': ids,
        }, headers=self.headers)

        data = res.json()
        data = data.get('data')

        for idKey in data.keys():
            el = data.get(idKey)
            name: str = el.get('name', '')
            maker_fee = el.get('maker_fee', 0)
            taker_fee = el.get('taker_fee', 0)

            fees: list[tuple] = []
            try:
                match name.lower():
                    case 'binance':
                        fees = self.findBinance() or []
                    case 'bybit':
                        fees = self.findByBit() or []
                    case 'okx':
                        fees = self.findOkx() or []
                    case 'kucoin':
                        fees = self.findKucoin() or []
            except Exception as e:
                logger.error(f'find error: {e}')

            if name is not None:
                liteDb.addExchange(
                    int(idKey), name, maker_fee, taker_fee, fees
                )

        logger.info('GET exhanges ENDED')
