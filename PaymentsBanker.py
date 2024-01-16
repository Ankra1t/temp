from telebot import TeleBot
from config_logger import logger
from flask import Response, Request

import math
import hmac
import json
from datetime import datetime

from typing import Callable
import requests
from db_new import db_new
from models import InvoiceBBanker, Transactions, UpdateBBanker, Price


class PaymentsBanker(object):
    """Класс обработки платежей, в том числе Cryptobot"""

    def __init__(self, api_key, api_secret, bot_instance:TeleBot) -> None:
        self.bot = bot_instance
        self.dt_format = "%Y-%m-%d %I:%M"
        self.token = api_key
        self.secret = api_secret
        self.method = 'POST'
        self.url = f"https://api.aws.bitbanker.org/latest/api/v1/invoices"
        self.firm_name_header = 'The Clan'
        self._handlers = []

    def set_field_invoice(self, attribute, value):
        target_dict = {
            'self': self,
        }
        target_obj = target_dict['self']
        if not hasattr(target_obj, attribute):
            print('Object {} does not have the "{}" attribute'.format(
                target_obj, attribute))
            return

        setattr(target_obj, attribute, value)

    def create_invoice(self, asset, amount, description, payer, data_payments=''):
        """Создание чека для оплаты синхронно
        через API Bitbanker
        """

        payment_currencies = ["USDT"]
        header = self.firm_name_header

        try:
            sign = self._create_sign(asset, amount, header, description)
        except Exception as e:
            logger.error(f'Ошибка sign в создании подписи [{e}]')

        params = {
            # ["USDT"] # BTC, ETH, ATOM, USDC, USDT, TRX
            "payment_currencies": payment_currencies,
            "currency": asset,  # "USDT"
            "amount": amount,
            "description": description,
            "header": header,
            "payer": payer,  # Ник или id из телеграмма
            "is_convert_payments": False,
            "data": {
                'description': description
            },  # data_payments
            "sign": sign,
        }

        json_data = json.dumps(params)

        logger.info(
            f'-----> Данные отправляемые при запросе счета в json, json_data: ')
        logger.info(json_data)

        print(f'params json_data')
        print(json_data)

        response = requests.post(
            self.url, headers={"X-API-KEY": self.token}, data=json_data)
        invoice: InvoiceBBanker = self._response_invoice(response)
        invoice.amount = amount
        invoice.asset = asset
        return invoice

    def _create_sign(self, currency, amount, header, description):
        """Создание подписи отдельно"""
        text = '{}{}{}{}'.format(
            currency, amount, header, description).encode('UTF-8')

        logger.info(
            f'-----> Сборка счета по параметрам currency, amount, header, description')
        logger.info(f'-----> currency [{currency}] ')
        logger.info(f'-----> amount [{amount}] ')
        logger.info(f'-----> header [{header}] ')
        logger.info(f'-----> description [{description}] ')
        logger.info(f'cтрока ={text}=')

        token = self.token.encode("UTF-8")

        signature = hmac.digest(token, text, 'sha256')

        logger.info(f'Подпись строки ={signature.hex()}=')

        return signature.hex()

    def _create_sign_secret(self, currency, amount, header, description):
        """Создание подписи отдельно"""
        text = '{}{}{}{}'.format(
            currency, amount, header, description).encode('UTF-8')

        logger.info(
            f'-----> Сборка счета по параметрам currency, amount, header, description')
        logger.info(f'-----> currency [{currency}] ')
        logger.info(f'-----> amount [{amount}] ')
        logger.info(f'-----> header [{header}] ')
        logger.info(f'-----> description [{description}] ')
        logger.info(f'cтрока ={text}=')

        secret = self.secret.encode("UTF-8")

        signature = hmac.digest(secret, text, 'sha256')

        logger.info(f'Подпись строки ={signature.hex()}=')

        return signature.hex()

    def _response_invoice(self, response):
        """Разобрать полученный ответ"""

        """ Успешный ответ запрос создания счета
        {
            "result": "success",    
            "id": "1izt8r3YNoZ6kgwewB3xCB",    
            "link": "https://app.bitbanker.org/external/invoice/1izt8r3YNoZ6kgwewB3xCB",   
            "addresses": {      
              "BTC": "1JxiDZYqFReWStvRy8tAm3LLFY9BaGrHZp"   
          }
        }
        """

        if response.status_code != 200:
            print(f'response.content ответ с ошибкой')
            print(response.content)
            response_json_err = response.json()
            if response_json_err.get("code"):
                code = response_json_err['code']
                raise Exception(f'Ошибка [{code}] BitBanker')

            raise Exception(
                f'Код ошибки [{response.status_code}] не корректный запрос к BitBanker')

        # Обработать json ответ
        response_json = response.json()

        print(f'response_json Обработанный json Ответ')
        print(response_json)

        if not response_json.get("result"):
            raise Exception(f'Проблемный ответ BitBanker нет поля \"result\"')

        invoice = InvoiceBBanker()
        invoice.invoice_id = response_json['id']
        invoice.pay_url = response_json['link']

        return invoice

    def get_params_payservice(self, subscribe_name):

        sub = {}
        subscribe_info = db_new.get_price_by_name(subscribe_name)

        if subscribe_info is None:
            return

        sub['sub_name'] = subscribe_name
        sub['amount'] = subscribe_info.price
        sub['currency'] = subscribe_info.currency
        sub['price_id'] = subscribe_info.id
        print(f'sub параметры услуги')
        print(sub)
        return sub

    def get_params_payservice_by_id(self, tariff_id):
        return db_new.get_price_by_id(tariff_id)

    def check_discount_price(self, tariff: Price):
        if tariff.discount is not None:
            now = datetime.now()
            fin_date_discount = tariff.discount.findate
            if fin_date_discount > now:
                # return tariff.price - ((tariff.price*tariff.discount.percent)/100))
                return math.ceil(tariff.price - ((tariff.price * tariff.discount.percent) / 100))
        return tariff.price

    def set_transactions_for_wait(self, user_id, iv: InvoiceBBanker, price_id):
        status = 'wait_payments'
        db_new.add_transaction(Transactions(
            user_id,
            code=str(iv.invoice_id),
            link=iv.pay_url,
            sum=iv.amount,
            currency=iv.asset,
            price_id=price_id,
            status=status
        ))

    def get_wait_transaction_for_complete(self, update: UpdateBBanker):
        invoice = update.payload

        # Ищем подписки только со статусом ожидания
        status = 'wait_payments'
        transaction_info = db_new.get_wait_transaction(
            str(invoice.invoice_id), status)

        print(f'transaction_info ')
        print(transaction_info)
        if transaction_info:
            return {
                'transaction_id': transaction_info.id,
                'user_id': transaction_info.user_id,
                'prices_id': transaction_info.price_id
            }
        return None

    def get_wait_transaction_by_invoice_id(self, invoice_id, asset):
        # Ищем подписки только со статусом ожидания
        status = 'wait_payments'
        transaction_info = db_new.get_wait_transaction(
            invoice_id, status)

        print(f'transaction_info ')
        print(transaction_info)
        if transaction_info:
            return {
                'transaction_id': transaction_info.id,
                'user_id': transaction_info.user_id,
                'prices_id': transaction_info.price_id,
                'sum': transaction_info.sum
            }
        return None

    def transactions_complete(self, transaction_id):
        db_new.set_transactions_complete(transaction_id)

    def get_updates(self, request: Request) -> Response:

        # Тестируем апдейт
        # logger.info(f'-----> Сработал update ')
        # return Response('Status OK!', status=200)

        body_text = request.stream.read()
        body = body_text.decode("UTF-8")
        incoming_update_json = json.loads(body)

        print(f'incoming_update_json ')
        print(incoming_update_json)
        logger.info(
            f'-----> incoming_update_json входящий json вебхук {incoming_update_json}')

        # Уведомление клиенту о его оплате
        if incoming_update_json['id'] and incoming_update_json['currency']:
            # Получаем пользователя по id счета, транзакции
            transaction = self.get_wait_transaction_by_invoice_id(
                incoming_update_json['id'], incoming_update_json['currency'])

        true_amount = incoming_update_json['amount']
        logger.info(f'-----> true_amount [{true_amount}]')

        if transaction:
            self.bot.send_message(transaction['user_id'],
                                  text='Благодарим. Получили информацию о вашем платеже',
                                  parse_mode="HTML")
            true_amount = int(transaction['sum'])

        if not incoming_update_json['sign'] or not incoming_update_json['sign_2']:
            logger.error(
                f'Ошибка [Не обнаружено полей подписей sign и sign_2 в вебхуке]')
            raise Exception(
                f'Ошибка получения полей сигнатуры sign или sign_2')

        print(f'incoming_update_json[\'data\'][\'description\'] ')
        print(incoming_update_json['data']['description'])

        try:
            signature_request = self._check_signature_request(
                bitbanker_signature=incoming_update_json['sign'],
                currency=incoming_update_json['currency'],
                amount=true_amount,
                header=self.firm_name_header,
                description=incoming_update_json['data']['description']
            )
        except Exception as e:
            logger.error(f'Ошибка в signature_request[{e}]')
            return Response('Error', 404)

        try:
            signature_webhook = self._check_signature_webhook(
                bitbanker_signature=incoming_update_json['sign_2'],
                currency=incoming_update_json['currency'],
                amount=true_amount,
                header=self.firm_name_header,
                description=incoming_update_json['data']['description']
            )
        except Exception as e:
            logger.error(f'Ошибка в signature_webhook[{e}]')
            return Response('Error', 404)

        # return Response('Status OK!', status=200)

        if signature_request and signature_webhook:

            update = UpdateBBanker()
            payload = InvoiceBBanker()

            payload.status = 'paid' if incoming_update_json['payed'] else incoming_update_json['payed']
            payload.invoice_id = incoming_update_json['id']
            payload.amount = incoming_update_json['payed_amount']
            payload.asset = incoming_update_json['currency']

            update.payload = payload

            for handler in self._handlers:
                logger.info(f'-----> Заполняем данные для апдейта ')
                handler(update)
                # handler(UpdateBBanker(**body))

            return Response('Status OK!', status=200)

        logger.info(f'-----> Сигнатуры не верны - апдейт не прошел ')

        if incoming_update_json['id'] and incoming_update_json['currency']:
            # Получаем пользователя по id счета, транзакции
            transaction = self.get_wait_transaction_by_invoice_id(
                incoming_update_json['id'], incoming_update_json['currency'])
            if transaction:
                self.bot.send_message(transaction['user_id'],
                                      text='Не смогли проверить корректность вашего платежа, обратитесь в нашу тех поддержку',
                                      parse_mode="HTML")

        return Response('Status False!', status=400)

        """
        {
          "payed": true,
          "id": "123456qwerty",
          "amount": 5000,
          "currency": "RUB",
          "payed_amount": 5000,
          "transactions": [
            {
              "tx_id": "sfsertert23425345342345345",
              "amount": 0.00015,
              "fee": 0.0000000025,
              "currency": "BTC"
            }
          ],
          "data": {},
          "sign": "requestsign", // подпись запроса вычисляется как (hmac(currency + amount + header + description, api_key, sha256))
          "sign_2": "webhooksign", // подпись запроса вычисляется как (hmac(currency + amount	+ header + description, api_secret, sha256))
        }
        """

    def _check_signature_request(self, bitbanker_signature: str, currency, amount, header, description) -> bool:

        self_sign = self._create_sign(currency, amount, header, description)

        print(f'сравнить _check_signature_request self_sign ')
        print(self_sign)

        print(f'и сравнить _check_signature_request bitbanker_signature ')
        print(bitbanker_signature)

        return hmac.compare_digest(self_sign, bitbanker_signature)

    def _check_signature_webhook(self, bitbanker_signature: str, currency, amount, header, description) -> bool:

        self_sign_2 = self._create_sign_secret(
            currency, amount, header, description)

        print(f'сравнить _check_signature_webhook self_sign ')
        print(self_sign_2)

        print(f'и сравнить _check_signature_webhook bitbanker_signature secret ')
        print(bitbanker_signature)

        return hmac.compare_digest(self_sign_2, bitbanker_signature)

    def pay_handler(self, func: Callable = None):
        def decorator(handler):
            self._handlers.append(handler)
            return handler

        return decorator
