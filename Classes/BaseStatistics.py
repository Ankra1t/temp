from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from datetime import timedelta

from config_logger import logger

from common.dt import get_datetime_now
from db import Database as DatabaseNew
from models import UserInfo, Purchase


class BaseStatistics(object):
    """Класс для работы с тарифами"""

    def __init__(self, db: DatabaseNew) -> None:
        self.db = db

    # # # # # # Вывод пользователей
    async def show_paid_users(self, bot: AsyncTeleBot, message : Message, period: str | None = None, product: str | None = None, start_to_fin: str | None = None):
        chat_id = message.chat.id

        if period:
            start_date, fin_date = self.get_dates_by_period(period)
            trans_list = self.db.get_paid_transactions_period(
                start_date, fin_date
            )
        elif product:
            trans_list = self.db.get_paid_transactions_product(product)
        elif start_to_fin:
            start_date, fin_date = start_to_fin.split('|')
            trans_list = self.db.get_paid_transactions_period(
                start_date, fin_date
            )
        else:
            trans_list = self.db.get_paid_transactions_all()

        if not trans_list:
            await bot.send_message(
                message.chat.id,
                'Оплат не обнаружено'
            )
            return False

        clients = {}
        for i in range(0, len(trans_list)):
            trans_item = trans_list[i]
            user_id = trans_item.user_id

            # Формируем покупку
            purchase = Purchase(
                user_id=user_id,
                price_name=trans_item.name,
                sum=trans_item.sum,
                currency=trans_item.currency,
                payment_date=trans_item.payment_date, # type: ignore
            )
            purchase_text = self.temp_client_purchase(purchase)
            full_purchases_text = clients[user_id] if clients.get(
                user_id) else ''
            clients[user_id] = "{}{}".format(
                full_purchases_text, purchase_text)

        logger.info(
            f"Выводим список клиентов кол-во tg_clients [{len(clients)}]")

        # Выводим список клиентов
        for i, el in enumerate(clients):
            user = self.db.get_user_by_id(el)
            if user is not None:
                msg = self.temp_client(user, str(clients.get(el)))
                await bot.send_message(chat_id, msg, reply_markup=None)
            else:
                logger.error(
                    f"Пользователь tg_id {el} не найден - оплаты по нему не выводим")

    # # # # # # Агрегаторы показателей

    def count_payments(self, period=None):
        """Кол-во платежей"""

        start_date, fin_date = self.get_dates_by_period(period)
        if not start_date or not fin_date:
            trans_list = self.db.get_paid_transactions_all()
        else:
            trans_list = self.db.get_paid_transactions_period(
                start_date, fin_date)

        return len(trans_list) if trans_list else 0

    def summ_by_transactions(self, period=None):
        """Суммы по всем транзакциям"""

        start_date, fin_date = self.get_dates_by_period(period)

        if not start_date or not fin_date:
            summ = self.db.get_paid_transactions_summ()
        else:
            summ = self.db.get_paid_transactions_summ_period(
                start_date, fin_date)
        return summ if summ else 0

    def count_by_product(self, product=None):
        """Кол-во платежей по каждому продукту"""
        if not product:
            return 0

        trans_list = self.db.get_paid_transactions_product(product)
        return len(trans_list) if trans_list else 0

    def summ_by_product(self, product):
        """Суммы платежей по каждому продукту"""
        if not product:
            return 0

        summ = self.db.get_paid_transactions_summ_product(product)
        return summ

    def count_payments_dry(self):
        """Кол-во плативших пользователей по транзакциям"""
        return self.db.get_paid_users_count()


    # # # # # # Специализированные показателей
    # # # # # # Шаблоны вывода
    def temp_client(self, user: UserInfo, purchases: str):
        """Вывести одного пользователя"""
        template = """
{} | <b>{} | {}</b>
{}
        """.format(user.id,
                   user.tg_id,
                   user.tg_username,
                   purchases
                   )
        return template

    def temp_client_purchase(self, purchase: Purchase):
        """Вывести одного пользователя"""
        payment_date_str = purchase.payment_date
        template = """
----------
Куплено: "{}"
Сумма: {} {}
Дата платежа: {}
        """.format(purchase.price_name,
                   purchase.sum,
                   purchase.currency,
                   payment_date_str
                   )
        return template

    # # # # # # Вспомогательные методы

    def get_dates_by_period(self, period):
        start_date = None
        fin_date = None

        fin_date = get_datetime_now()
        now = get_datetime_now()
        if period == 'today':
            start_date = now - timedelta(days=1)
        if period == 'week':
            start_date = now - timedelta(days=7)
        if period == 'month':
            start_date = now - timedelta(days=30)
        if period == 'half_year':
            start_date = now - timedelta(days=30 * 6)
        if period == 'year':
            start_date = now - timedelta(days=365)

        return start_date, fin_date
