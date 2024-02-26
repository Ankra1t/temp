from telebot import TeleBot
from datetime import timedelta

from initialize import logger


from common.dt import get_datetime_now, get_str_by_datetime
from keyboard_inlines import Admin_kb_inlines
from db_new import db_new, Database as DatabaseNew
from models import Price, Discount, Client, UserInfo, Transactions, Subscribe, Purchase


class BaseStatistics(object):
    """Класс для работы с тарифами"""

    def __init__(self, db: DatabaseNew, bot_instance: TeleBot) -> None:
        self.db = db
        self.bot = bot_instance

    # # # # # # Вывод пользователей
    def show_paid_users(self, message, period:str = None, product: str = None, start_to_fin: str = None):
        chat_id = message.chat.id

        if period:
            start_date, fin_date = self.get_dates_by_period(period)
            trans_list = self.db.get_paid_transactions_period(start_date, fin_date )
        elif product:
            trans_list = self.db.get_paid_transactions_product(product)
        elif start_to_fin:
            start_date, fin_date = start_to_fin.split('|')
            trans_list = self.db.get_paid_transactions_period(start_date, fin_date)
        else:
            trans_list = self.db.get_paid_transactions_all()

        if not trans_list:
            self.bot.send_message(
                message.chat.id,
                'Оплат не обнаружено'
            )
            return False

        tg_clients = {}
        logger.info(f"Обрабатываем транзакции len(trans_list) [{len(trans_list)}]")
        for i in range(0, len(trans_list)):
            trans_item = trans_list[i]
            tg_id = trans_item.user_id

            # Формируем покупку
            price = self.db.get_price_by_id(trans_item.price_id, None)
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

        logger.info(f"Выводим список клиентов кол-во tg_clients [{len(tg_clients)}]")

        # Выводим список клиентов
        for i, el in enumerate(tg_clients):
            user = self.db.get_user_by_tg_id(el)
            if user is not None:
                msg = self.temp_client(user, tg_clients.get(el))
                self.bot.send_message(chat_id, msg, reply_markup=None)
            else:
                logger.error(f"Пользователь tg_id {el} не найден - оплаты по нему не выводим")

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
            summ = self.db.get_paid_transactions_summ_period(start_date, fin_date)
        print(f'период {period} summ [{summ}]')
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
        trans_list = self.db.get_paid_transactions_all_dry_users()
        return len(trans_list) if trans_list else 0

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
        payment_date_str = get_str_by_datetime(purchase.payment_date)
        template = """
----------
Куплено: "{}"
Сумма: {} {}
Дата платежа: {}
        """.format(purchase.price_name,
                   purchase.real_sum,
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

