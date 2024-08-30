from telebot.async_telebot import AsyncTeleBot, types
from db import db
from models import Price
from common.dt import get_datetime_now, get_str_by_datetime


class TariffManager(object):
    """Класс для работы с тарифами"""

    def __init__(self) -> None:
        pass

    async def admin_discount_list(self, bot: AsyncTeleBot, message: types.Message, type_discount='active'):
        list = db.get_prices(True)
        count = 0
        if len(list) == 0:
            await bot.send_message(
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
                await bot.send_message(
                    message.chat.id,
                    desc_template,
                )

            # Сортируем прошедшие скидки
            if type_discount == 'inactive' and self.is_inactive_discount(tariff):
                count = count + 1
                desc_template = self.get_template_discount_show(tariff)
                await bot.send_message(
                    message.chat.id,
                    desc_template,
                )
        if not count:
            empty_message = 'Активных' if type_discount == 'active' else 'Прошедших'
            await bot.send_message(
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
