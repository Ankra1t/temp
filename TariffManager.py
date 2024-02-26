from telebot import types, TeleBot
from datetime import datetime

from keyboard_inlines import Admin_kb_inlines
from db_new import db_new
from models import Price, Discount
from common.dt import get_datetime_now, get_str_by_datetime


class TariffManager(object):
    """Класс для работы с тарифами"""

    def __init__(self, bot_instance: TeleBot, kb_inl_instance: Admin_kb_inlines, kb_inl_user_instance) -> None:
        self.bot = bot_instance
        self.kb_inl = kb_inl_instance
        self.kb_inl_user = kb_inl_user_instance

    def deactivate_tariff(self, tariff_id):
        db_new.deactive_price(tariff_id)
        
    def on_off_tariff(self, tariff_id: int):
        """Переключить тариф с одного положения на другое"""
        switch = db_new.check_switch_tariff(tariff_id)
        switch_put = 0 if switch else 1

        if switch_put == 1:
            # Если тариф включается, то обновляем дату окончания тарифа - значение null
            self.set_findate_tariff(tariff_id, None)


        db_new.switch_tariff(tariff_id, switch_put)

        return switch_put

    def set_findate_tariff(self, tariff_id, findate):
        db_new.set_findate_tariff(tariff_id, findate)

    def switch_off_finish_tariffs(self):
        """Отключить тарифы с истекшим сроком"""
        today = get_datetime_now()
        db_new.switch_off_finish_tariffs(today)

    def set_discount_tariff(self, id: int, discount: Discount):
        db_new.set_price_discount(
            id, discount.percent, discount.findate)

    def admin_tariff_list_show(self, message: types.Message, mode='main', user_id=None, product_id=None):
        list = None

        # Перед показом тарифов отключить те, у которых закончился срок действия
        self.switch_off_finish_tariffs()

        if product_id:
            list = db_new.get_prices_by_product(product_id, 1, None)
        else:
            list = db_new.get_prices(1, None)

        if len(list) == 0:
            self.bot.send_message(
                message.chat.id,
                'Тарифов не обнаружено'
            )
            return

        for i in range(0, len(list)):

            tariff = list[i]


            desc_template = self.get_template_tariff_show_admin(tariff)
            on_off_label = 'Отключить ⭕️' if tariff.switch_active == 1 else 'Включить ☑️'
            if mode == 'main':
                kb = self.kb_inl.kb_tariff_options(tariff.id, on_off_label=on_off_label)
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

    def admin_tariff_list_custom_show(self, chat_id, mode='choose_subscribe', product_id=None):
        tariff_list = None

        # Перед показом тарифов отключить те, у которых закончился срок действия
        self.switch_off_finish_tariffs()
        print(f'Здесь выключили тарифы с истекшим сроком действия ')
        if product_id:
            tariff_list = db_new.get_prices_by_product(product_id, 1, switch_active=1)
        else:
            tariff_list = db_new.get_prices(1, switch_active=1)

        if not tariff_list:
            return False

        for i in range(0, len(tariff_list)):

            tariff = tariff_list[i]
            if mode == 'choose_subscribe':
                desc_template = self.get_template_tariff_choose_for_user_show(tariff)
                kb = self.kb_inl.kb_tariff_choose_for_user(tariff.id)

                self.bot.send_message(
                    chat_id,
                    desc_template,
                    reply_markup=kb
                )

        return True


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
        date_now = get_datetime_now()
        if tariff.discount:
            if tariff.discount.percent > 0 and tariff.discount.findate > date_now:
                return True

        return False

    def is_inactive_discount(self, tariff):
        date_now = get_datetime_now()
        if tariff.discount:
            if tariff.discount.percent > 0 and tariff.discount.findate < date_now:
                return True

        return False

    def tariff_list_show(self, message: types.Message, product_id=None):
        list = None

        # Перед показом тарифов отключить те, у которых закончился срок действия
        self.switch_off_finish_tariffs()

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
                now = get_datetime_now()
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
        findate = get_str_by_datetime(tariff.discount.findate)
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
    
    def get_template_tariff_choose_for_user_show(self, tariff: Price):
        """Получить краткое описание тарифа """
        template = """
<b>id={} "{}"</b>
Продукт "{}" (<i>стандартно действует {} дн.</i>)
                """.format(tariff.id,
                           tariff.name,
                           tariff.type_product,
                           tariff.duration_days
                           )
        return template

