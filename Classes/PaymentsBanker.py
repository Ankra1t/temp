import hmac
import json
import requests
from telebot import TeleBot
from flask import Response, Request

from Classes.GuardPaymentAccess import GuardPaymentAccess
from NOTIFIER import notifier
from NOTIFIER.messages import mess_user_paid

from common.dt import get_str_by_datetime
from common.utils import check_discount_price
from db import db
from config_logger import logger
from messages.users import paid_subscribe_msg
from models import InvoiceBBanker, Price, UpdateBBanker


class PaymentsBanker(object):
    """Класс обработки платежей, в том числе BitBanker"""

    def __init__(self, api_key: str, api_secret: str, bot_instance: TeleBot, pay_guard: GuardPaymentAccess) -> None:
        self.bot = bot_instance
        self.token = api_key
        self.secret = api_secret
        self.method = 'POST'
        self.url = f"https://api.aws.bitbanker.org/latest/api/v1/invoices"
        self.header = 'ProfMarkets'
        self.pay_guard = pay_guard

    # # # # # # # Создание платежа
    # !!! Need to change
    def create_invoice(self, user_id: int, tariff: Price):
        """
            Создание чека для оплаты синхронно через API Bitbanker
        """
        payment_currencies = ["USDT"]

        if tariff.price_crypto == 0:
            return False

        user = db.get_user_by_tg_id(user_id)
        if user is None:
            return False

        price = check_discount_price(tariff, 'crypto')

        try:
            sign = self._create_sign(
                tariff.currency_crypto, price, self.header, '-'
            )
        except Exception as e:
            return False

        params = {
            "payment_currencies": payment_currencies,
            "currency": tariff.currency_crypto,
            "amount": price,
            "description": '-',
            "header": self.header,
            "payer": user.username or user.tg_id,
            "is_convert_payments": False,
            "data": {},
            "sign": sign,
        }

        response = requests.post(
            self.url,
            headers={"X-API-KEY": self.token},
            data=json.dumps(params)
        )

        if response.status_code < 200 or response.status_code >= 300:
            return False

        body = response.json()
        print(body)

    def _response_invoice(self, response):
        if response.status_code != 200:
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

    def get_params_payservice_by_id(self, tariff_id):
        return db.get_price_by_id(tariff_id)

    # # # # # # # Получение Webhooks

    def get_updates(self, request: Request) -> Response:
        body: dict | None = request.get_json(True, True)
        if body is None:
            return Response(status=400)

        if body.get('id') and body.get('currency'):
            transaction = self.get_wait_transaction_by_invoice_id(
                body['id'], body['currency']
            )

        true_amount = body['amount']

        if transaction:
            self.bot.send_message(
                transaction['user_id'],
                'Благодарим. Получили информацию о вашем платеже'
            )
            true_amount = int(transaction['sum'])

        if not body['sign'] or not body['sign_2']:
            logger.error(
                f'Ошибка [Не обнаружено полей подписей sign и sign_2 в вебхуке]')
            return Response(status=400)

        try:
            signature_request = self._check_signature_request(
                bitbanker_signature=body['sign'],
                currency=body['currency'],
                amount=true_amount,
                header=self.header,
                description=body['data']['description']
            )
        except Exception as e:
            logger.error(f'Ошибка в signature_request {e}')
            return Response('Error', 404)

        try:
            signature_webhook = self._check_signature_webhook(
                bitbanker_signature=body['sign_2'],
                currency=body['currency'],
                amount=true_amount,
                header=self.header,
                description=body['data']['description']
            )
        except Exception as e:
            logger.error(f'Ошибка в signature_webhook[{e}]')
            return Response('Error', 404)

        # return Response('Status OK!', status=200)

        if signature_request and signature_webhook:
            update = UpdateBBanker()
            payload = InvoiceBBanker()

            payload.status = 'paid' if body['payed'] else body['payed']
            payload.invoice_id = body['id']
            payload.amount = body['payed_amount']
            payload.asset = body['currency']

            update.payload = payload

            self.invoice_paid(update)

            return Response('Status OK!', status=200)

        logger.info(f'-----> Сигнатуры не верны - апдейт не прошел ')

        if body['id'] and body['currency']:
            # Получаем пользователя по id счета, транзакции
            transaction = self.get_wait_transaction_by_invoice_id(
                body['id'], body['currency'])
            if transaction:
                self.bot.send_message(
                    transaction['user_id'],
                    'Не смогли проверить корректность вашего платежа, обратитесь в нашу тех поддержку'
                )

        return Response('Status False!', status=400)

    def _check_signature_request(self, bitbanker_signature: str, currency, amount, header, description) -> bool:
        self_sign = self._create_sign(currency, amount, header, description)

        return hmac.compare_digest(self_sign, bitbanker_signature)

    def _check_signature_webhook(self, bitbanker_signature: str, currency, amount, header, description) -> bool:
        self_sign_2 = self._create_sign_secret(
            currency, amount, header, description)

        return hmac.compare_digest(self_sign_2, bitbanker_signature)

    # # # # # # # Транзакции
    def get_wait_transaction_by_invoice_id(self, invoice_id, asset):
        # Ищем подписки только со статусом ожидания
        transaction_info = db.get_wait_transaction(invoice_id)

        if transaction_info:
            return {
                'transaction_id': transaction_info.id,
                'user_id': transaction_info.user_id,
                'sum': transaction_info.sum
            }
        return None

    def transactions_complete(self, transaction_id):
        db.success_transaction(transaction_id)

    def set_transactions_for_wait(self, user_id, iv: InvoiceBBanker, price_id):
        price = db.get_price_by_id(price_id)
        if price is None:
            return

        db.add_transaction(
            user_id,
            str(iv.invoice_id),
            iv.pay_url,
            iv.amount or 0,
            'wait_payments',
            iv.asset or '',
            price.name,
            price.duration_days,
            price.type_product
        )

    def get_wait_transaction_for_complete(self, update: UpdateBBanker):
        invoice = update.payload

        # Ищем подписки только со статусом ожидания
        transaction = db.get_wait_transaction(
            str(invoice.invoice_id)  # type: ignore
        )

        return transaction

    # # # # # # # Служебные
    def _create_sign(self, currency, amount, header, description):
        """Создание подписи отдельно"""
        text = f'{currency}{amount}{header}{description}'.encode()
        signature = hmac.digest(self.token.encode("UTF-8"), text, 'sha256')
        return signature.hex()

    def _create_sign_secret(self, currency, amount, header, description):
        """Создание подписи отдельно"""
        text = f'{currency}{amount}{header}{description}'.encode('UTF-8')
        signature = hmac.digest(self.secret.encode("UTF-8"), text, 'sha256')
        return signature.hex()

    def invoice_paid(self, update: UpdateBBanker) -> None:
        if update.payload is None:
            return

        # return True;
        # Найти по invoice_id транзакцию
        if update.payload.status == 'paid':

            transaction = self.get_wait_transaction_for_complete(update)

            if transaction:
                logger.info('-----> Нашли нужную транзакцию '
                            'далее transactions_complete [{}]'.format(transaction.id))

                self.bot.send_message(
                    transaction.user_id,
                    'Ваш платеж подтвержден и находиться в обработке'
                )

                # Завершаем транзакцию
                self.transactions_complete(transaction.id)

                # Добавить платную подписку
                finish_date_obj = self.pay_guard.set_paid_subscribe(transaction)
                finish_date = get_str_by_datetime(finish_date_obj)

                logger.info(f'-----> Добавили пользователю платную подписку')

                # Обнуляем пробную подписку
                self.pay_guard.deactivate_user_trial_subscribe(
                    transaction.user_id
                )

                # Отправляем сообщение пользователю
                self.bot.send_message(
                    transaction.user_id,
                    text=paid_subscribe_msg(
                        finish_date, transaction.name
                    ),
                )

                # Сообщение в бот уведомлений об оплате
                summ_full = f"{transaction.sum} {transaction.currency}"

                user = db.get_user_by_tg_id(transaction.user_id)
                if user is not None:
                    notifier.send_notification('text', mess_user_paid(
                        user_id=user.id,
                        user_nike='@' + user.username if user.username else user.tg_id,
                        summ_paid=summ_full,
                        tariff_name=transaction.name,
                        finish_date=finish_date
                    ))

            else:
                logger.error(f'-----> Не нашли транзакцию по параметрам чека {update.payload} '
                             f'и статусу status "wait_payments"  ')
