from telebot import types
from datetime import timedelta

from handlers.AdminHandler import get_start_date_cancel_subscribe, get_user_for_cancel_subscribe
from initialize import bot, kb_inl_admin, pay_guard, tariff_manager
import variables as vars
from models import User

from common.utils import set_state_data
from common.dt import get_str_by_datetime

from MAIN.callbacks import (
    kb_admin_users_back, kb_admin_choose_periods, send_admin_main
)
from MAIN.states import AdminUsersState

from cb_filters import (admin_default_factory, adm_action)
from config_logger import logger


@bot.callback_query_handler(func=None, admin_default=admin_default_factory.filter())
def admin_default_callbacks(call: types.CallbackQuery):
    callback_data = admin_default_factory.parse(call.data)
    type = callback_data.get('type', '')

    chat_id = call.message.chat.id
    mes_id = call.message.id
    user_id = call.from_user.id

    # ## Добавить _ кол-во дней к подписке
    if type == 'add_days_subscribe':
        with bot.retrieve_data(user_id, chat_id) as data:
            user: User = data.get('user')

        fin_date = pay_guard.update_user_subscribe_findate(user, 'add')

        show_fin_date = '-'
        if fin_date is not None:
            show_fin_date = get_str_by_datetime(fin_date)

        bot.send_message(
            chat_id,
            f'Подписка клиента id {user.id} удачно изменена, новая дата {show_fin_date}',
            reply_markup=kb_admin_users_back()
        )
        bot.delete_state(user_id, chat_id)

    # ## Отменить подписку за период
    if type == 'subscribe_cancel_time':
        logger.info(f'-----> Выбрано меню ***{type}*** ')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='Отменить подписку за период', reply_markup=kb_inl_admin.users_cancel_subscribe_time())

    # ## Отменить подписку за прошедший час
    if type == 'cancel_subscribe_hour':
        logger.info(f'-----> Выбрано меню ***{type}*** ')

        date_show = pay_guard.cancel_subscribes_for_time_type('hours', 1)
        bot.send_message(call.message.chat.id,
                         text='Все подписки с {} по {} были отменены'.format(date_show['time_start'],
                                                                             date_show['time_end']),
                         reply_markup=kb_admin_users_back())

    # ## Отменить подписку за прошедший день
    if type == 'cancel_subscribe_day':
        logger.info(f'-----> Выбрано меню ***{type}*** ')

        date_show = pay_guard.cancel_subscribes_for_time_type('days', 1)
        bot.send_message(call.message.chat.id,
                         text='Все подписки с {} по {} были отменены'.format(date_show['time_start'],
                                                                             date_show['time_end']),
                         reply_markup=kb_admin_users_back())

    # ## Отменить подписку за выбранный период
    if type == 'cancel_subscribe_period':
        logger.info(f'-----> Выбрано меню ***{type}*** ')

        bot.send_message(call.message.chat.id,
                         text=f'Отправьте "ДАТУ ОТ" в формате DD.MM.YYYY', reply_markup=kb_admin_users_back())

        bot.register_next_step_handler(
            call.message, get_start_date_cancel_subscribe)

    # ## Отменить подписку пользователю
    if type == 'subscribe_cancel_user':
        logger.info(f'-----> Выбрано меню ***{type}*** ')

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='Отправьте username пользователя для отмены его текущей подписки',
                              reply_markup=kb_admin_users_back())

        bot.register_next_step_handler(
            call.message, get_user_for_cancel_subscribe)

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=None, action=adm_action.filter())
def admin_action_callbacks(call: types.CallbackQuery):
    callback_data: dict = adm_action.parse(call.data)
    action, target_id = callback_data['action'], callback_data['id']
    logger.info(f'Кнопка callback_query ***{action}***')
    logger.info(f'Элемент id ***{target_id}***')

    chat_id = call.message.chat.id
    mes_id = call.message.id
    user_id = call.from_user.id

    # ##### ------------------ Отменить подписку для пользователя
    # [deprecated - реализовано в другом функционале с State состояниями]
    if action == 'user_cancel_subscribe':
        # !! установить tariff_id
        pay_guard.set_subscribe_unactive_by_user_id(target_id)
        user = vars.user_dict[call.message.chat.id]
        bot.send_message(chat_id=call.message.chat.id,
                         text=f'У пользователя {user.username} id {user.id} убрали активную подписку',
                         reply_markup=kb_admin_users_back())

        # Сбросить обработчик приема username
        bot.clear_step_handler(call.message)

    # ##### ------------------ Пользователи - Отменить - Выбрать другую
    if action == 'admin_change_subscribe_for_user':
        user = vars.user_dict[call.message.chat.id]

        # Показать список текущих тарифов с кнопкой Установить пользователю
        tariff_manager.admin_tariff_list_show(
            call.message, mode='change_for_client', user_id=user.id)

    # ##### ------------------ Назначить новый тариф для пользователя
    if action == 'admin_set_tariff_client':
        # Запросить кол-во дней или выбрать период
        bot.set_state(user_id, AdminUsersState.subscribe_days, chat_id)
        set_state_data(bot, user_id, chat_id, {
            'tariff_id': target_id,
        })
        bot.send_message(chat_id,
                         text='Введите <b>количество дней</b> подписки, или выберите период:',
                         reply_markup=kb_admin_choose_periods())

