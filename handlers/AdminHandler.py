from telebot import types
from datetime import datetime
from config_logger import logger

from initialize import bot, kb_inl_admin, pay_guard
from models import User
from db import db

from MAIN.callbacks.admin.users.keyboards import kb_admin_users_back
import variables as vars


# Отменить подписку за период
def get_start_date_cancel_subscribe(message: types.Message):
    logger.info(
        f'-----> Получили ДАТУ ОТ которой отменить подписку date_start')
    date_start = message.text or ''

    if date_start:
        date_start_obj = datetime.strptime(date_start, '%d.%m.%Y')

        bot.send_message(chat_id=message.chat.id,
                         text=f'Отправьте "ДАТУ ДО" в формате DD.MM.YYYY',
                         reply_markup=kb_admin_users_back())
        bot.register_next_step_handler(
            message, get_end_date_cancel_subscribe, date_start_obj)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=f'Дата введена некорректно!\n\nОтправьте "ДАТУ ОТ" в формате DD.MM.YYYY',
                         reply_markup=kb_admin_users_back())
        bot.register_next_step_handler(
            message, get_start_date_cancel_subscribe)


def get_end_date_cancel_subscribe(message: types.Message, date_start_obj):
    logger.info(
        f'-----> Получили ДАТУ ДО которой отменить подписку date_start')
    date_end = message.text or ''

    if date_end:
        date_end_obj = datetime.strptime(date_end, '%d.%m.%Y')

        date_show = pay_guard.cancel_subscribes_for_time_period(
            date_start_obj, date_end_obj)
        bot.send_message(message.chat.id,
                         text='Все подписки с {} по {} были отменены'.format(date_show['time_start'],
                                                                             date_show['time_end']),
                         reply_markup=kb_admin_users_back())

    else:
        bot.send_message(chat_id=message.chat.id,
                         text=f'Дата введена некорректно!\n\nОтправьте "ДАТУ ДО" в формате DD.MM.YYYY',
                         reply_markup=kb_admin_users_back())
        bot.register_next_step_handler(
            message, get_end_date_cancel_subscribe)


def get_user_for_cancel_subscribe(message: types.Message):
    logger.info(
        f'-----> Получили username пользователя для деактивации его подписки ')
    username = (message.text or '').replace('@', '')

    # Проверяем есть данный пользователь в базе
    user_id = db.get_user_id_by_tg_name(username)
    if user_id:
        user = User()
        user.id = user_id
        user.username = username
        vars.user_dict[message.chat.id] = user
        bot.send_message(chat_id=message.chat.id,
                         text='Что делаем с подпиской?',
                         reply_markup=kb_inl_admin.users_cancel_subscribe_user(user.id))

    else:
        bot.send_message(chat_id=message.chat.id,
                         text=f'Такого пользователя не существует, попробуйте другой username',
                         reply_markup=kb_admin_users_back())
        bot.register_next_step_handler(
            message, get_user_for_cancel_subscribe)

