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

    def admin_tariff_list_show(self, message: types.Message, mode='main', user_id=None):
        list = db_new.get_prices(1)
        if len(list) == 0:
            self.bot.send_message(chat_id=message.chat.id,
                                  parse_mode="HTML",
                                  text=f'Тарифов не обнаружено')
            return

        for i in range(0, len(list)):
            tariff = list[i]

            desc_template = self.get_template_tariff_show(tariff)
            if mode == 'main':
                kb = self.kb_inl.kb_tariff_options(tariff.id)
            else: # 'change_for_client'
                kb = self.kb_inl.kb_tariff_options_choose(
                    f'{user_id}_{tariff.id}')

            if tariff.img:

                self.bot.send_photo(chat_id=message.chat.id, photo=tariff.img,
                                    caption=desc_template,
                                    parse_mode="HTML", reply_markup=kb)
            else:
                self.bot.send_message(chat_id=message.chat.id,
                                      parse_mode="HTML",
                                      text=desc_template,
                                      reply_markup=kb)

    def admin_discount_list_active(self, message: types.Message):
        list = db_new.get_prices(1)

        if len(list) == 0:
            self.bot.send_message(chat_id=message.chat.id,
                                  parse_mode="HTML",
                                  text=f'Тарифов не обнаружено')
            return

        for i in range(0, len(list)):
            tariff = list[i]

            # Сортируем действующие скидки
            if self.is_active_discount(tariff):
                desc_template = self.get_template_discount_show(tariff)

                self.bot.send_message(chat_id=message.chat.id,
                                      parse_mode="HTML",
                                      text=desc_template,
                                      )

    def is_active_discount(self, tariff):
        print(f'is_active_discount == tariff ')
        print(tariff)
        discount_percent = tariff
        discount_findate = ''
        tariff_name = ''
        tariff_id = ''
        return True

        pass

    def tariff_list_show(self, message: types.Message):
        list = db_new.get_prices(1)
        if len(list):
            self.bot.send_message(chat_id=message.chat.id,
                                  parse_mode="HTML",
                                  text=f'Тарифов не обнаружено')
        for i in range(0, len(list)):
            tariff = list[i]
            discount_show = ''
            if tariff.discount is not None:
                now = datetime.now()
                fin_date_discount = tariff.discount.findate
                if fin_date_discount > now:
                    discount_show = f'\n\n<b>Скидка {str(round(tariff.discount.percent))}%</b>'

            desc_template = self.get_template_tariff_show(tariff)
            if tariff.img:
                try:
                    self.bot.send_photo(chat_id=message.chat.id,
                                        photo=tariff.img,
                                        caption=desc_template + discount_show,
                                        reply_markup=self.kb_inl_user.kb_pay(tariff.id, message.from_user.id))
                except Exception as e:
                    # print(f'Что то пошло не так {e}')
                    pass
                    # logger.error(f'Ошибка  [{e}]')
            else:
                self.bot.send_message(chat_id=message.chat.id,
                                      text=desc_template + discount_show,
                                      reply_markup=self.kb_inl_user.kb_pay(tariff.id, message.from_user.id))

    def get_template_tariff_show(self, tariff: Price):
        """Получить описание согласно шаблону и данным тарифа """
        template = """
{}
{} {}
{}
        """.format(tariff.name, str(tariff.price), tariff.currency, tariff.description)
        return template

    def get_template_discount_show(self, tariff: Price):
        """Получить описание согласно шаблону и данным тарифа """
        template = """
{}
{} {}
{}
        """.format(tariff.name, str(tariff.price), tariff.currency, tariff.description)
        return template
