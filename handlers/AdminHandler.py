from telebot import types
from datetime import datetime
from config_logger import logger

from initialize import bot, text_editor, kb_inl_admin, pay_guard
from models import User

from MAIN.callbacks.admin.users.keyboards import kb_admin_users_back
import variables as vars


# Редактирование текстов
def admin_edit_text(message: types.Message, text_id: int):
    logger.info(
        '-----> Получили username пользователя для установки нужной подписки ')

    try:
        text_editor.save_content(text_id, message.text)
    except Exception as e:
        logger.error(f'Ошибка TextEditor.save_content [{e}]')

    bot.send_message(message.chat.id, f'Текс под id={text_id} сохранен ...',
                     reply_markup=kb_inl_admin.kb_edit_single_text_updated())


# Отменить подписку за период
def get_start_date_cancel_subscribe(message: types.Message):
    logger.info(
        f'-----> Получили ДАТУ ОТ которой отменить подписку date_start')
    date_start = (message.text or '').strip()

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
    date_end = (message.text or '').strip()

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
    username = (message.text or '').strip().replace('@', '')

    # Проверяем есть данный пользователь в базе
    user_id = pay_guard.get_user_id_by_username(username)
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


# Изменить тех. поддержку
def update_support(message: types.Message):
    vars.sup_name = message.text
    bot.send_message(message.chat.id, f'Новый аккаунт тех.поддерки: {vars.sup_name} ?',
                     reply_markup=kb_inl_admin.workers_choice('update_support'))
