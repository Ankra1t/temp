from telebot import types, TeleBot
from datetime import datetime

from keyboard_inlines import Admin_kb_inlines
from db import Database
from db_new import db_new
from models import Price, Discount


class TariffManager(object):
    """Класс для работы с тарифами"""

    def __init__(self, db: Database, bot_instance: TeleBot, kb_inl_instance: Admin_kb_inlines, kb_inl_user_instance) -> None:
        self.db = db
        self.bot = bot_instance
        self.kb_inl = kb_inl_instance
        self.kb_inl_user = kb_inl_user_instance
        self.dt_format = "%Y-%m-%d %I:%M"
        self.dt_format_admin_show = "%d/%m/%Y %I:%M"
        self.dt_format_user_show = "%d/%m/%Y"

    def deactivate_tariff(self, tariff_id):
        db_new.deactive_price(tariff_id)

    def set_discount_tariff(self, id: int, discount: Discount):
        db_new.set_price_discount(
            id, discount.percent, discount.findate)

    def admin_tariff_list_show(self, message: types.Message, mode='main', user_id=None, product_id=None):
        list = None
        if product_id:
            list = db_new.get_prices_by_product(product_id, 1)
        else:
            list = db_new.get_prices(1)

        if len(list) == 0:
            self.bot.send_message(
                message.chat.id,
                'Тарифов не обнаружено'
            )
            return

        for i in range(0, len(list)):

            tariff = list[i]
            desc_template = self.get_template_tariff_show_admin(tariff)
            if mode == 'main':
                kb = self.kb_inl.kb_tariff_options(tariff.id)
            else:  # 'change_for_client'
                kb = self.kb_inl.kb_tariff_options_choose(
                    f'{user_id}_{tariff.id}')

            try:
                if tariff.img:

                    self.bot.send_photo(
                        message.chat.id, tariff.img,
                        desc_template,
                        reply_markup=kb
                    )
                else:
                    self.bot.send_message(
                        message.chat.id,
                        desc_template,
                        reply_markup=kb
                    )

            except Exception as e:
                print(
                    f'Проблемы с отправкой тарифа admin_tariff_list_show {e}')
                if 'wrong file identifier' in str(e):
                    print(
                        f'Скорей всего не отправилась картинка созданная в другом боте')

    def admin_discount_list(self, message: types.Message, type_discount='active'):
        list = db_new.get_prices(1)
        count = 0
        if len(list) == 0:
            self.bot.send_message(
                message.chat.id,
                f'Тарифов не обнаружено'
            )
            return
        for i in range(0, len(list)):
            tariff = list[i]

            # Сортируем действующие скидки
            if type_discount == 'active' and self.is_active_discount(tariff):
                count = count + 1
                desc_template = self.get_template_discount_show(tariff)
                self.bot.send_message(
                    message.chat.id,
                    desc_template,
                )

            # Сортируем прошедшие скидки
            if type_discount == 'inactive' and self.is_inactive_discount(tariff):
                count = count + 1
                desc_template = self.get_template_discount_show(tariff)
                self.bot.send_message(
                    message.chat.id,
                    desc_template,
                )
        if not count:
            empty_message = 'Активных' if type_discount == 'active' else 'Прошедших'
            self.bot.send_message(
                message.chat.id,
                f'{empty_message} скидок в тарифах не обнаружено',
            )

    def is_active_discount(self, tariff):
        date_now = datetime.now()
        if tariff.discount:
            if tariff.discount.percent > 0 and tariff.discount.findate > date_now:
                return True

        return False

    def is_inactive_discount(self, tariff):
        date_now = datetime.now()
        if tariff.discount:
            if tariff.discount.percent > 0 and tariff.discount.findate < date_now:
                return True

        return False

    def tariff_list_show(self, message: types.Message, product_id=None):
        list = None
        if product_id:
            list = db_new.get_prices_by_product(product_id, 1)
        else:
            list = db_new.get_prices(1)

        if len(list) == 0:

            self.bot.send_message(
                message.chat.id,
                'Тарифов не обнаружено'
            )

        for i in range(0, len(list)):
            tariff = list[i]
            discount_show = ''
            if tariff.discount is not None:
                now = datetime.now()
                fin_date_discount = tariff.discount.findate
                if fin_date_discount > now:
                    discount_show = f'\n\n<b>Скидка {str(round(tariff.discount.percent))}%</b>'

            desc_template = self.get_template_tariff_show(tariff)

            try:
                if tariff.img:
                    self.bot.send_photo(chat_id=message.chat.id,
                                        photo=tariff.img,
                                        caption=desc_template + discount_show,
                                        reply_markup=self.kb_inl_user.kb_pay(tariff.id))
                else:
                    self.bot.send_message(chat_id=message.chat.id,
                                          text=desc_template + discount_show,
                                          reply_markup=self.kb_inl_user.kb_pay(tariff.id))

            except Exception as e:
                print(f'Проблемы с отправкой тарифа tariff_list_show {e}')
                if 'wrong file identifier' in str(e):
                    print(
                        f'Скорей всего не отправилась картинка созданная в другом боте')

    def change_fields_tariff_show(self, tariff_id, change_text):
        tariff = db_new.get_price_by_id(tariff_id)
        return self.get_template_change_tariff_show(tariff, change_text)

    def get_template_tariff_show_admin(self, tariff: Price):
        """Получить описание согласно шаблону и данным тарифа """
        template = """
{}
{} {}
{}
Продукт "{}"
<i>действует {} дн.</i>
        """.format(tariff.name,
                   str(tariff.price),
                   tariff.currency,
                   tariff.description,
                   tariff.type_product,
                   tariff.duration_days
                   )
        return template

    def get_template_discount_show(self, tariff: Price):
        """Получить описание согласно шаблону и данным тарифа """
        findate = tariff.discount.findate.strftime(self.dt_format_admin_show)
        template = """
id {} <b>{}</b> (стоимость {} {})
<b>скидка {}%</b> до {}
        """.format(tariff.id,
                   tariff.name,
                   str(tariff.price),
                   tariff.currency,
                   tariff.discount.percent,
                   findate
                   )
        return template

    def get_template_change_tariff_show(self, tariff: Price, change_text):
        """Получить описание согласно шаблону и данным тарифа """
        template = """
id={} <b>\"{}\"</b>
{} {}
{}
<i>действует {} дн.</i>

<b>{}</b>
        """.format(tariff.id,
                   tariff.name,
                   str(tariff.price),
                   tariff.currency,
                   tariff.description,
                   tariff.duration_days,
                   change_text
                   )
        return template

    def get_template_tariff_show(self, tariff: Price):
        """Получить описание согласно шаблону и данным тарифа для клиента """
        template = """
{}
{} {}
{}
<i>действует {} дн.</i>
        """.format(tariff.name, str(tariff.price), tariff.currency, tariff.description, tariff.duration_days)
        return template
