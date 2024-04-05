from config_logger import logger
from flask import Response, Request

from hmac import HMAC
from hashlib import sha256
import json

from db import db
from typing import Callable
import requests
from models import Invoice, Update


class Payments(object):
    """Класс обработки платежей, в том числе Cryptobot"""

    def __init__(self, token, network) -> None:
        self.token = token
        self.network = network
        self.method = 'GET'
        self.url = f"{self.network}/api/createInvoice"
        self._handlers = []

    def create_invoice(self, asset, amount, description):
        """Создание чека для оплаты синхронно
        через API cryptobot
        """

        # result = requests.get("https://requestb.in")
        # print(f'result https://requestb.in')
        # asset = "USDT"
        # amount = "0.1"
        # description = "Оплата подписки"
        params = {
            "asset": asset,
            "amount": amount,
            "description": description,
            # "hidden_message": hidden_message,
            # "paid_btn_name": paid_btn_name,
            # "paid_btn_url": paid_btn_url,
            # "payload": payload,
            # "allow_comments": allow_comments,
            # "allow_anonymous": allow_anonymous,
            # "expires_in": expires_in,
        }

        for key, value in params.copy().items():
            if isinstance(value, bool):
                params[key] = str(value).lower()
            if value is None:
                del params[key]

        response = requests.get(
            self.url, headers={"Crypto-Pay-API-Token": self.token}, params=params)
        logger.info(f'-----> Запрос чека прошел удачно response [{response}]')

        # print(f'Запрос к {self.url} response | response.text')
        # print(response)
        # print(response.text)

        return self._response_invoice(response)

    def _response_invoice(self, response):
        """Разобрать полученный ответ"""

        if response.status_code != 200:
            # name = response["error"]["name"]
            # code = response["error"]["code"]
            raise Exception('Какая то проблема с ответом от Cryptobot')

        # Обработать json ответ
        response_json = response.json()
        # print(f'response_json Обработанный json Ответ')
        # print(response_json)

        if not response_json.get("ok"):
            name = response["error"]["name"]
            code = response["error"]["code"]
            raise Exception(
                f'Проблемный ответ криптобота name [{name}] code [{code}]')

        # print(f'response_json.get[result] ')
        # print(response_json['result'])

        return Invoice(**response_json['result'])

    def set_transactions_for_wait(self, user_id: int, iv: Invoice, price_id: int):
        tariff = db.get_price_by_id(price_id)
        if tariff is None:
            return

        db.add_transaction(
            user_id,
            str(iv.invoice_id),
            iv.pay_url,
            iv.amount,
            'wait_payments',
            iv.asset,
            tariff.name,
            tariff.duration_days,
            tariff.type_product
        )

    def get_wait_transaction_for_complete(self, update: Update):
        invoice = update.payload

        # Ищем подписки только со статусом ожидания
        transaction = db.get_wait_transaction(str(invoice.invoice_id))

        # if transaction_info is not None:
        #     return {
        #         'transaction_id': transaction_info.id,
        #         'user_id': transaction_info.user_id,
        #         'prices_id': transaction_info.price_id
        #     }
        # return None
        if transaction:
            return transaction
        return None

    def transactions_complete(self, transaction_id):
        db.success_transaction(transaction_id)

    def get_updates(self, request: Request) -> Response:
        """
        WebHook updates route

        Args:
            request (Request): WebHook request

        Returns:
            Response: 200 status code for cryptopay api
        """
        logger.info(f'-----> Сработал update ')
        body_text = request.stream.read()
        body = body_text.decode("UTF-8")
        body = json.loads(body)

        crypto_pay_signature = request.headers.get(
            "Crypto-Pay-Api-Signature", "No value"
        )

        try:
            signature = self.check_signature(
                body_text=body, crypto_pay_signature=crypto_pay_signature
            )
        except Exception as e:
            logger.error(f'Ошибка в check_signature[{e}]')
            return Response('ERROR', 400)

        if signature:
            for handler in self._handlers:
                logger.info(f'-----> Получилось!!  body:::')
                handler(Update(**body))
                # handler(Update(**body), request.app)
            return Response('Status OK!', status=200)

        logger.info(f'-----> Неправильная сигнатура запроса, что-то поменять ')
        return Response('ERROR', 400)

    def get_updates_check(self, update: Update):
        for handler in self._handlers:
            logger.info(f'!! Дернули все зареганные обработчики')
            handler(update)

    def check_signature(self, body_text: str, crypto_pay_signature: str) -> bool:
        """
        https://help.crypt.bot/crypto-pay-api#verifying-webhook-updates

        Args:
            body_text (str): webhook update body
            crypto_pay_signature (str): Crypto-Pay-Api-Signature header

        Returns:
            bool: is cryptopay api signature
        """
        token = sha256(string=self.token.encode("UTF-8")).digest()
        signature = HMAC(
            key=token, msg=body_text, digestmod=sha256  # type: ignore
            # key=token, msg=body_text.encode("UTF-8"), digestmod=sha256
        ).hexdigest()
        # logger.info(f'-----> Получили сигнатуру signature  [{signature}]')
        # logger.info(f'-----> Сравни с crypto_pay_signature [{crypto_pay_signature}]')

        return signature == crypto_pay_signature

    def pay_handler(self, func: Callable | None = None):
        def decorator(handler):
            self._handlers.append(handler)
            return handler

        return decorator
