from telebot import TeleBot
from math import floor
from time import sleep
from CALCULATE.common.messages import msg_calculate_result
from MAIN.common.utils import get_print_signal_info
from common.utils import get_calculation

from config_logger import logger, log_send_fails, log_send_no_send, log_send_ok
from db_new import db_new
from initialize import bot
from models import Post


def send_message_by_type(
    bot: TeleBot,
    user_id: int,
    type: str,
    text: str,
    media_id: str | None
):
    if type == 'photo':
        bot.send_photo(
            user_id, media_id,
            caption=text
        )
    elif type == 'video':
        bot.send_video(
            user_id, media_id,
            caption=text
        )
    else:
        bot.send_message(user_id, text)


def get_post_content(post: Post, user_id: int) -> tuple[str, str | None]:
    signal_text = ''
    calc_text = None

    details = post.details
    if details:
        open_price = details.open_price
        stop_loss = details.stop_loss
        name = details.name
        ticker = details.ticker

        signal_text = f'<b>{name}</b>\n'
        calc_text = f'<b>{name}</b>\n'

        signal_text += f'👉 {ticker}\n'

        signal_text += get_print_signal_info(
            open_price, stop_loss
        )

        user_db_id = db_new.get_user_id_by_tg_id(user_id)
        user_base_values = db_new.get_user_base(user_db_id)
        dep = user_base_values['base_deposit']
        risk = user_base_values['base_risk_percent']

        if dep is None or risk is None:
            calc_text = 'Для получения расчетов по сигналу введите все базовые значения в настройках калькулятора'
        else:
            count_bet = floor(
                (dep * risk / 100) /
                (open_price - stop_loss)
            )
            summary_open_value = round(count_bet * open_price, 2)

            credit = 1
            if summary_open_value > dep:
                credit = round(summary_open_value // dep + 1)

            calc_text = '<b><u>Расчет по сигналу</u></b>\n'
            count_bet, value_bet, credit, risk_value, take_profit, profit = get_calculation(
                user_id, dep, risk, open_price,
                stop_loss, ticker
            )

            mes = msg_calculate_result(
                user_id, dep, risk, open_price,
                stop_loss, count_bet, value_bet, credit,
                risk_value, take_profit, profit
            )

    signal_text += '\n\n' + post.content

    return signal_text, calc_text


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
        log_send_ok.info(f'Начало рассылки------------------>>>')

        if calc_test:
            users = db_new.get_all_users()
            users = list(map(lambda x: x.tg_id, users))
        else:
            users = self.users

        i = 0
        while i < len(users):
            user = users[i]

            if current_batch < self.c_tg:
                try:
                    i += 1
                    self.send_by_type(user)
                    current_batch += 1
                except Exception as e:
                    err_mess = f'Ошибка пользователя {user} : {e}'
                    print(err_mess)
                    log_send_fails.error(err_mess)
            else:
                sleep(1)
                current_batch = 0

    def send_by_type(self, id: int):
        content, calc_mes = get_post_content(self.post, id)

        send_message_by_type(
            bot,
            id,
            self.post.mes_type,
            content,
            self.post.media
        )

        if calc_mes is not None:
            bot.send_message(id, calc_mes)
