from telebot.async_telebot import AsyncTeleBot
from datetime import timedelta
import time
import threading

from Classes.BlockTGBotSender import BlockTGBotSender, send_message_by_type
from Classes import pay_guard, coinmarketService

from common.dt import get_datetime_now
from common.utils import get_lang
from messages.users import end_paid_subscribe_msg, end_trial_subscribe_msg
from config_logger import logger
from db import db
from models import Post


def _check_future_post_for_sent(bot: AsyncTeleBot):
    lose_hours = 4
    date_now = get_datetime_now()
    lose_time_back = date_now - timedelta(hours=lose_hours)

    mas_posts = db.get_all_posts()

    for post in mas_posts:
        if (post.date_time is not None) and (post.date_time < date_now) and (post.date_time > lose_time_back):
            _send_future_post_by_intime(bot, post)
            db.delete_post(post.id or 0)

            # TODO - Написать админу, что отложенный пост отправлен
            time.sleep(10)

    return True


def _send_future_post_by_intime(bot: AsyncTeleBot, post: Post):
    """Рассылка отложенных постов по времени"""
    users_id = list(map(lambda user: user.tg_id, pay_guard.get_paid_users()))

    try:
        tgsender = BlockTGBotSender(bot, users_id, post)
        tgsender.send()
    except Exception as e:
        logger.error(
            f'Ошибка -send_future_pos_by_intime- в балансировщике при рассылке [{e}]')
    pass


# TODO - через класс рассылок
async def _check_finish_trial_subscribe(bot: AsyncTeleBot):
    users = pay_guard.get_users_note_fin_trial()
    if len(users) == 0:
        return

    for user in users:
        try:
            lang = get_lang(user.tg_id)
            await send_message_by_type(
                bot, user.tg_id, 'text', end_trial_subscribe_msg(lang)
            )
        except Exception as e:
            logger.error(f'[end_trail_sub error sending message]: {e}')

    pay_guard.set_subscribe_unactive_many_users()


# TODO - через класс рассылок
async def _check_finish_paid_subscribe(bot: AsyncTeleBot):
    users = pay_guard.get_users_note_fin_paid()
    if len(users) == 0:
        return

    for user in users:
        try:
            lang = get_lang(user.tg_id)
            await send_message_by_type(
                bot, user.tg_id, 'text', end_paid_subscribe_msg(lang)
            )
        except Exception as e:
            logger.error(f'[end_paid_sub error sending message]: {e}')

    # После рассылки убрать активность ПЛАТНЫХ рассылок у данных пользователей
    pay_guard.set_paid_subscribe_unactive_many_users()


def _check_tariff():
    db.check_tariffs_datetime()


# Проверка рассылок каждые 30 сек - в отдельном потоке
def _check_infinite_tasks(bot: AsyncTeleBot):
    sleep_time_check = 60
    while True:
        # _check_finish_paid_subscribe(bot)
        # _check_finish_trial_subscribe(bot)
        # _check_tariff()
        time.sleep(sleep_time_check)

def _check_exchanges():
    sleep_time_check = 60 * 60 * 12
    while True:
        try:
            coinmarketService.get()
        except:
            pass
        time.sleep(sleep_time_check)


def run_thread(bot: AsyncTeleBot):
    threading.Thread(
        target=_check_infinite_tasks, args=(bot,), name='check_unfinit_tasks'
    ).start()
    # threading.Thread(
    #     target=_check_exchanges, name='_check_exchanges'
    # ).start()
