from telebot import types, TeleBot
from datetime import datetime, timedelta

from keyboard_inlines import Admin_kb_inlines
from db_new import db_new, Database as DatabaseNew
from models import Price, Discount, Client, UserInfo, Transactions, Subscribe, Purchase


class BaseStatistics(object):
    """Класс для работы с тарифами"""

    def __init__(self, db: DatabaseNew, bot_instance: TeleBot) -> None:
        self.db = db
        self.bot = bot_instance

        self.dt_format = "%Y-%m-%d %I:%M"
        self.dt_format_admin_show = "%d/%m/%Y %I:%M"
        self.dt_format_user_show = "%d/%m/%Y"

    # # # # # # Вывод пользователей

    def show_paid_users(self, message):
        chat_id = message.chat.id
        trans_list = self.db.get_paid_transactions_all()

        if not trans_list:
            self.bot.send_message(
                message.chat.id,
                'Оплат не обнаружено'
            )

        tg_clients = {}
        for i in range(0, len(trans_list)):
            trans_item = trans_list[i]
            tg_id = trans_item.user_id

            # Формируем покупку
            price = self.db.get_price_by_id(trans_item.price_id)
            purchase = Purchase(
                user_id=tg_id,
                price_name=price.name,
                real_sum=trans_item.sum,
                currency=price.currency,
                payment_date=trans_item.payment_date,
            )
            purchase_text = self.temp_client_purchase(purchase)
            full_purchases_text = tg_clients[tg_id] if tg_clients.get(
                tg_id) else ''
            tg_clients[tg_id] = "{}{}".format(
                full_purchases_text, purchase_text)

        # Выводим список клиентов
        for i, el in enumerate(tg_clients):
            user = self.db.get_user_by_tg_id(el)
            if user is not None:
                msg = self.temp_client(user, tg_clients.get(el))
                self.bot.send_message(chat_id, msg, reply_markup=None)

    # # # # # # Агрегаторы показателей

    def count_payments(self, period=None):
        """Кол-во подписок"""
        # Считаем кол-во транзакций
        start_date = None
        fin_date = None

        fin_date = datetime.utcnow()
        now = datetime.now()
        if period == 'today':
            fin_date = now - timedelta(days=1)
        if period == 'week':
            fin_date = now - timedelta(days=7)
        if period == 'month':
            fin_date = now - timedelta(days=30)
        if period == 'half_year':
            fin_date = now - timedelta(days=30 * 6)
        if period == 'year':
            fin_date = now - timedelta(days=365)

        if not start_date and not fin_date:
            trans_list = self.db.get_paid_transactions_all()
        else:
            trans_list = self.db.get_paid_transactions_period(
                start_date, fin_date)

        return len(trans_list) if trans_list else 0

    def summ_by_transactions(self):
        """Суммы по всем транзакциям"""
        # Считаем кол-во транзакций
        summ = self.db.get_paid_transactions_summ()
        return summ

    # # # # # # Специализированные показателей

    # # # # # # Шаблоны вывода

    def temp_client(self, user: UserInfo, purchases: str):
        """Вывести одного пользователя"""
        template = """
{} | <b>{} | {}</b>
{}
        """.format(user.id,
                   user.tg_id,
                   user.username,
                   purchases
                   )
        return template

    def temp_client_purchase(self, purchase: Purchase):
        """Вывести одного пользователя"""
        template = """
----------
Куплено: "{}"
Сумма: {} {}
Дата платежа: {}
        """.format(purchase.price_name,
                   purchase.real_sum,
                   purchase.currency,
                   purchase.payment_date
                   )
        return template

    def temp_block_users(self, users, count=8):
        """Вывести пользователей блоками"""
        template = """
{}
                """.format()
        return template

    # # # # # # Вспомогательные методы
    def get_client_by_transaction(self, trans: Transactions):
        pass
