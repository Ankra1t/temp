from telebot import types, TeleBot
from datetime import datetime

from keyboard_inlines import Admin_kb_inlines
from db import db
from models import Price
from common.dt import get_datetime_now, get_str_by_datetime


class TariffManager(object):
    """Класс для работы с тарифами"""

    def __init__(self, bot_instance: TeleBot, kb_inl_instance: Admin_kb_inlines) -> None:
        self.bot = bot_instance
        self.kb_inl = kb_inl_instance

    def admin_tariff_list_show(self, message: types.Message, mode='main', user_id=None, product_id=None):
        list = None

        if product_id:
            list = db.get_prices_by_product(product_id, 1, None)
        else:
            list = db.get_prices(1, None)

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
                kb = None
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

        if product_id:
            tariff_list = db.get_prices_by_product(
                product_id, 1, switch_active=1)
        else:
            tariff_list = db.get_prices(1, switch_active=1)

        if not tariff_list:
            return False

        for i in range(0, len(tariff_list)):

            tariff = tariff_list[i]
            if mode == 'choose_subscribe':
                desc_template = self.get_template_tariff_choose_for_user_show(
                    tariff)
                kb = self.kb_inl.kb_tariff_choose_for_user(tariff.id)

                self.bot.send_message(
                    chat_id,
                    desc_template,
                    reply_markup=kb
                )

        return True

    def admin_discount_list(self, message: types.Message, type_discount='active'):
        list = db.get_prices(1)
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
        dt = tariff.discount.findate if (
            tariff.discount is not None) else get_datetime_now()
        findate = get_str_by_datetime(dt)

        percent = tariff.discount.percent if (
            tariff.discount is not None) else 0

        template = """
id {} <b>{}</b> (стоимость {} {})
<b>скидка {}%</b> до {}
        """.format(tariff.id,
                   tariff.name,
                   str(tariff.price),
                   tariff.currency,
                   percent,
                   findate
                   )
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
