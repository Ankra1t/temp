from math import floor
from time import sleep
from MAIN.common.utils import get_print_signal_info

from config_logger import logger
from db import db
from db_new import db_new
from initialize import bot
from CALCULATE.common.messages import msg_calculate_result
from models import Post


class BlockTGBotSender(object):
    """Класс для рассылки сообщений через бота Telebot согласно ограничений API TG"""

    def __init__(
            self, users: list[int], post: Post
    ):
        # Ограничение телеграм на кол-во сообщений разным пользователям в сек (с запасом)
        self.c_tg = 25

        self.users = users
        self.post = post

    def send(self):
        self.batch_send(True)

    def batch_send(self, calc_test=False):
        current_batch = 0
        logger.info(f'Начало рассылки------------------>>>')

        if calc_test:
            users = db_new.get_all_users()
            users = list(map(lambda x: x.tg_id, users))
        else:
            users = self.users

        i = 0
        while i < len(users):
            user = users[i]
            current_batch += 1

            if current_batch < self.c_tg:
                try:
                    self.bot_send_by_type(user)
                    i += 1
                except Exception as e:
                    print(f'Ошибка пользователя {user}: {e}')
            else:
                sleep(1)
                current_batch = 0

    def bot_send_by_type(self, id: int):
        signal_text = ''
        calc_text = ''

        if self.post.details:
            open_price = self.post.details.open_price
            stop_loss = self.post.details.stop_loss
            name = self.post.details.name
            ticker = self.post.details.ticker

            signal_text += f'<b>{name}</b>\n'
            signal_text += f'👉 {ticker}\n'

            calc_text = f'<b>{name}</b>\n'

            signal_text += get_print_signal_info(
                open_price, stop_loss
            )

            user_base_values = db.get_user_base(id)
            dep = user_base_values['base_deposit']
            risk = user_base_values['base_risk_percent']

            if dep is None or risk is None:
                calc_text = 'Для получения расчетов по сигналу введите все базовые значения в настройках калькулятора'
            else:
                diff = open_price - stop_loss
                tp_1 = open_price + diff * 3
                tp_2 = open_price + diff * 4
                tp_3 = open_price + diff * 5

                count_bet = floor(
                    (dep * risk / 100) /
                    (open_price - stop_loss)
                )
                summary_open_value = round(count_bet * open_price, 2)

                credit = 1
                if summary_open_value > dep:
                    credit = round(summary_open_value // dep + 1)

                calc_text = '<b><u>Расчет по сигналу</u></b>\n'
                calc_text += msg_calculate_result(
                    id, dep, risk,
                    open_price,
                    stop_loss,
                    tp_1, tp_2, tp_3,
                    count_bet,
                    summary_open_value,
                    credit, dep * risk
                )

        try:
            media = self.post.media
            content = signal_text + '\n\n' + self.post.content
            if self.post.mes_type == 'photo':
                bot.send_photo(
                    id, media,
                    caption=content
                )
            elif self.post.mes_type == 'text':
                bot.send_message(id, content)
            elif self.post.mes_type == 'video':
                bot.send_video(
                    id, media,
                    caption=content
                )

            bot.send_message(id, calc_text)
        except Exception as e:
            print(f'Ошибка рассылки user({id}): {e}')
            pass
