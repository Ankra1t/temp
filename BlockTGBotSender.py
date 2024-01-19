from math import floor
from time import sleep
from common.utils import get_decimal_count, get_print_float

from config_logger import logger
from db import db
from initialize import bot
from CALCULATE.common.messages import msg_calculate_result


class BlockTGBotSender(object):
    """Класс для рассылки сообщений через бота Telebot согласно ограничений API TG"""

    def __init__(
            self, users: list[int], text: str,
            media: str, kind: str,
            open_price: float | None = None,
            stop_loss: float | None = None,
            name: str | None = None,
            ticker: str | None = None
    ):
        # Ограничение телеграм на кол-во сообщений разным пользователям в сек (с запасом)
        self.c_tg = 25

        self.users = users
        self.text = text
        self.media = media
        self.kind = kind
        self.name = name

        self.open_price = open_price or 0
        self.stop_loss = stop_loss or 0
        self.ticker = ticker

    def send(self):
        self.batch_send(True)

    def simple_send(self):
        """Старая рассылка от Ильи не учитывает ТГ ограничения и не оптимизирован код"""
        if 'photo' in self.media:
            for i in range(0, len(self.users)):
                try:
                    out_file = self.media.replace('(photo)', '')
                    bot.send_photo(
                        self.users[i], photo=out_file, caption=self.text)
                except Exception as e:
                    print(f'Ошибка пользователя {self.users[i]}')
        elif 'text' in self.media:
            for i in range(0, len(self.users)):
                try:
                    bot.send_message(self.users[i], self.text)
                except Exception as e:
                    print(f'Ошибка пользователя {self.users[i]}')
        elif 'video' in self.media:
            for i in range(0, len(self.users)):
                try:
                    out_file = self.media.replace('(video)', '')
                    bot.send_video(
                        self.users[i], video=out_file, caption=self.text)
                except Exception as e:
                    print(f'Ошибка пользователя {self.users[i]}')

    def batch_send(self, calc_test=False):
        current_batch = 0
        logger.info(f'Начало рассылки------------------>>>')

        if calc_test:
            users = db.get_all_users()
            users = list(map(lambda x: int(x[9]), users))
        else:
            users = self.users

        i = 0
        while i < len(users):
            user = users[i]
            current_batch += 1

            if current_batch < self.c_tg:
                i += 1
                try:
                    self.bot_send_by_type(user)
                except Exception as e:
                    print(f'Ошибка пользователя {user}: {e}')
            else:
                sleep(1)
                current_batch = 0

    def bot_send_by_type(self, id: int):
        signal_text = f'<b>{self.name}</b>\n' if self.name is not None else ''
        signal_text += (f'👉 {self.ticker}\n' if self.ticker is not None else '')

        calc_text = f'<b>{self.name}</b>\n' if self.name is not None else ''

        if self.kind == 'signal':
            round_count = max(get_decimal_count(self.open_price),
                              get_decimal_count(self.stop_loss))

            signal_text += f'Цена входа: <b>{get_print_float(self.open_price, round_count)}</b>\n'
            signal_text += f'Стоп лосс: <b>{get_print_float(self.stop_loss, round_count)}</b>\n'

            user_base_values = db.get_user_base(id)
            dep = user_base_values['base_deposit']
            risk = user_base_values['base_risk_percent']

            if dep is None or risk is None:
                calc_text = 'Для получения расчетов по сигналу введите все базовые значения в настройках калькулятора'
            else:
                diff = self.open_price - self.stop_loss
                tp_1 = self.open_price + diff * 3
                tp_2 = self.open_price + diff * 4
                tp_3 = self.open_price + diff * 5

                count_bet = floor(
                    (dep * risk / 100) /
                    (self.open_price - self.stop_loss)
                )
                summary_open_value = round(count_bet * self.open_price, 2)

                credit = 1
                if summary_open_value > dep:
                    credit = round(summary_open_value // dep + 1)

                calc_text = '<b><u>Расчет по сигналу</u></b>\n'
                calc_text += msg_calculate_result(
                    id, dep, risk,
                    self.open_price,
                    self.stop_loss,
                    tp_1, tp_2, tp_3,
                    count_bet,
                    summary_open_value,
                    credit, dep * risk
                )

        try:
            content = signal_text + '\n' + self.text
            if '(photo)' in self.media:
                out_file = self.media.replace('(photo)', '')
                bot.send_photo(
                    id, out_file,
                    caption=content
                )
            elif '(text)' in self.media:
                bot.send_message(id, content)
            elif '(video)' in self.media:
                out_file = self.media.replace('(video)', '')
                bot.send_video(
                    id, out_file,
                    caption=content
                )

            bot.send_message(id, calc_text)
        except Exception as e:
            print(f'Ошибка рассылки user({id}): {e}')
            pass
