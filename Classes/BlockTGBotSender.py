from typing import Optional
from telebot import TeleBot
from time import sleep
from CALCULATE.common.messages import msg_calculate_result
from MAIN.common.utils import get_print_signal_info

from config_logger import log_send_fails, log_send_ok
from db import db

from initialize import bot, pay_guard
from models import Calculation, Post, UserInfo


def send_message_by_type(
    bot: TeleBot,
    user_id: int,
    type: str,
    text: str,
    media_id: Optional[str] = None
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

        user_db_id = db.get_user_id_by_tg_id(user_id)
        u_base = db.get_calc_user_settings(user_db_id)

        if u_base is None or (u_base.deposit is None or u_base.risk is None):
            calc_text = 'Для получения расчетов по рекомендации введите все базовые значения в настройках калькулятора'
        else:
            if u_base.risk[1]:
                risk_value = u_base.deposit * u_base.risk[0] * 0.01
            else:
                risk_value = u_base.risk[0]

            calc_text = '<b><u>Расчет по рекомендации</u></b>\n'

            calc_info = Calculation(
                user_id=0,
                deposit=u_base.deposit,
                risk_value=risk_value,
                open_price=open_price,
                stop_loss=stop_loss,
                currency=ticker,
                market='crypto',  # !
                tp_ratio=u_base.tp_ratio,
                split_values=u_base.split_values,
                trading_style='-'
            )

            calc_text += msg_calculate_result(user_id, calc_info)

    signal_text += '\n\n' + post.content

    return signal_text, calc_text


class BlockTGBotSender(object):
    """Класс для рассылки сообщений через бота Telebot согласно ограничений API TG"""

    def __init__(
            self, users: list[int], post: Post
    ):
        # Ограничение телеграм на кол-во сообщений разным пользователям в сек (с запасом)
        self.c_tg = 26
        # Кол-во сообщений на одного пользователя
        self.c_by_user = 2
        # Безопасная пауза
        self.p_by_user = 0.01

        self.users = users
        self.post = post

    def send(self):
        self.batch_send(True)

    def batch_send(self, calc_test=False):
        current_batch = 0
        if calc_test:
            users = db.get_all_users()

            users_info = users
            users = list(map(lambda x: x.tg_id, users))
        else:
            users = self.users

        i = 0
        while i < len(users):
            user = users[i]
            user_i: UserInfo = users_info[i]

            if current_batch < self.c_tg:
                username = '@' + user_i.username if user_i.username else 'Скрыт'
                try:
                    i += 1
                    self.send_by_type(user)
                    current_batch += self.c_by_user
                    log_send_ok.info(
                        f'Отправлено tg_id{user} db_id{user_i.id} username->{username} ')
                except Exception as e:
                    err_mess = f'Ошибка пользователя tg_id{user} db_id{user_i.id} username->{username} : {e}'
                    print(err_mess)
                    log_send_fails.error(err_mess)
                sleep(self.p_by_user)
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
