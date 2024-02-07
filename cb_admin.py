from telebot import types
from datetime import datetime
from handlers.AdminHandler import admin_edit_text, get_start_date_cancel_subscribe, get_user_for_cancel_subscribe


from initialize import bot, kb_inl_admin, text_editor, pay_guard, tariff_manager, base_statis
from messages.workers import admin_users_msg, admin_fut_posts_msg, menu_msg
from messages.statistics import admin_main_statistics
import variables as vars
from models import User
from db_new import db_new

from messages.workers import admin_main_msg
from common.utils import set_state_data
from MAIN.callbacks import (
    kb_params, kb_posts, kb_admin_users,
    kb_admin_users_back, kb_admin_workers_back,
    send_admin_workers, kb_statistics,
    kb_statistics_back
)
from MAIN.states import AdminTariffState

from cb_filters import (admin_default_factory, adm_action, admin_main_factory)
from config_logger import logger


@bot.callback_query_handler(func=None, admin_main=admin_main_factory.filter())
def admin_main_callbacks(call: types.CallbackQuery):
    callback_data: dict = admin_main_factory.parse(call.data)
    type = callback_data['type']
    logger.info(f'Кастомное callback_query меню ***{type}***')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id
    message = call.message

    if type == 'users':
        logger.info(f'-----> Нажали меню пользователи ')
        count_all = db_new.get_users_count()
        count_with_sub = len(pay_guard.get_paid_users())
        count_old = len(pay_guard.get_paid_more1_users())

        text = admin_users_msg(count_all, count_with_sub, count_old)

        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_admin_users()
        )

    if type == 'workers':
        send_admin_workers(bot, call.message, user_id)

    if type == 'fut_posts':
        bot.edit_message_text(
            admin_fut_posts_msg(), chat_id, mes_id,
            reply_markup=kb_posts()
        )

    if type == 'tariffs':
        bot.edit_message_text('Действия с тарифами', chat_id, mes_id,
                              reply_markup=kb_inl_admin.kb_tariffs())

    if type == 'params':
        bot.edit_message_text(
            menu_msg('Параметры'), chat_id, mes_id,
            reply_markup=kb_params()
        )

    if type == 'payment':

        # Общие Показатели
        count_subscribes = base_statis.count_payments()
        summ_all_users = base_statis.summ_by_transactions()

        bot.edit_message_text(
            admin_main_statistics(count_subscribes, summ_all_users), chat_id, mes_id,
            reply_markup=kb_statistics()
        )

        # Вывести всех участников по транзакциям
    #     Вывести оплаченные транзакции


    bot.clear_step_handler(call.message)
    bot.delete_state(user_id, chat_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=None, admin_default=admin_default_factory.filter())
def admin_default_callbacks(call: types.CallbackQuery):
    callback_data = admin_default_factory.parse(call.data)
    type = callback_data.get('type', '')

    chat_id = call.message.chat.id
    mes_id = call.message.id
    user_id = call.from_user.id

    # ## Главное меню
    if type == 'go_main':
        logger.info(f'-----> Выбрано меню ***{type}*** ')
        try:
            count_all = db_new.get_users_count()
            count_with_sub = len(pay_guard.get_paid_users())
            count_old = len(pay_guard.get_paid_more1_users())
            count_admins = len(db_new.get_all_workes())
            count_fut_posts = len(db_new.get_all_posts())

            text = admin_main_msg(count_all, count_with_sub,
                                  count_old, count_admins, count_fut_posts)

            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb_inl_admin.main()
            )

            bot.clear_step_handler(call.message)
        except Exception as e:
            logger.error(f'Ошибка type_menu == go_main[{e}]')

    # ## Добавить _ кол-во дней к подписке
    if type == 'add_days_subscribe':
        with bot.retrieve_data(user_id, chat_id) as data:
            user: User = data.get('user')

        fin_date = pay_guard.update_user_subscribe_findate(user, 'add')

        finish_date_obj = datetime.strptime(fin_date or '', '%Y-%m-%d %H:%M')
        fin_date = finish_date_obj.strftime('%d/%m/%Y')

        bot.send_message(
            chat_id,
            f'Подписка клиента id {user.id} удачно изменена, новая дата {fin_date}',
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

    # ## Добавить новый тариф Тарифы - Добавить тариф
    # if type == 'add_tariff':
    #     logger.info(f'-----> Выбрано меню ***{type}*** ')
    #
    #     bot.edit_message_text(
    #         'Введите название нового тарифа (заголовок)', chat_id, mes_id,
    #         reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
    #
    #     bot.set_state(user_id, AdminTariffState.name, chat_id)

    if type == 'add_tariff':
        logger.info(f'-----> Выбрано меню ***{type}*** ')

        bot.edit_message_text(
            'Укажите продукт тарифа', chat_id, mes_id,
            reply_markup=kb_inl_admin.kb_choice_product())

        # bot.set_state(user_id, AdminTariffState.name, chat_id)

    # ## Выбрать продукт для показа тарифов по нему
    if type == 'tariffs_list':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=f'Выберите продукт для показа тарифов', reply_markup=kb_inl_admin.kb_select_tariff_products())

    # ## Показать список всех тарифов
    if type == 'tariffs_list_all':
        logger.info(f'-----> Выбрано меню ***{type}*** ')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=f'Список всех добавленных тарифов', reply_markup=None)
        tariff_manager.admin_tariff_list_show(call.message)

        bot.send_message(call.message.chat.id,
                         text=f'Выполнение действий с тарифами', reply_markup=kb_inl_admin.kb_tariff_list())

    # ## Показать список тарифов по продукту
    # if type == 'tariffs_list_all':
    #     logger.info(f'-----> Выбрано меню ***{type}*** ')
    #     bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
    #                           text=f'Список всех добавленных тарифов', reply_markup=None)
    #     tariff_manager.admin_tariff_list_show(call.message)
    #
    #     bot.send_message(call.message.chat.id,
    #                      text=f'Выполнение действий с тарифами', reply_markup=kb_inl_admin.kb_tariff_list())

    # ## Показать список действующих скидок
    if type == 'discount_list_active':
        logger.info(f'-----> Выбрано меню ***{type}*** ')
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
        #                       text=f'--- Список действующих скидок:', reply_markup=None)

        bot.send_message(call.message.chat.id,
                         text=f'--- Список действующих скидок:', reply_markup=None)
        tariff_manager.admin_discount_list(
            call.message, type_discount='active')

        bot.send_message(call.message.chat.id,
                         text=f'Выполнение действий с тарифами', reply_markup=kb_inl_admin.kb_tariff_list())

    # ## Показать список Прошедших скидок
    if type == 'discount_list_inactive':
        logger.info(f'-----> Выбрано меню ***{type}*** ')
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
        #                       text=f'--- Список прошедших скидок:', reply_markup=None)
        bot.send_message(call.message.chat.id,
                         text=f'--- Список прошедших скидок:', reply_markup=None)
        tariff_manager.admin_discount_list(
            call.message, type_discount='inactive')

        bot.send_message(call.message.chat.id,
                         text=f'Выполнение действий с тарифами', reply_markup=kb_inl_admin.kb_tariff_list())

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

    # ##### ------------------ Редактируем сообщения из БД
    if action == 'edit_bot_text':
        logger.info(f'-----> Действие ***{action}*** ')

        # Спрятать reply клаву
        bot.send_message(chat_id=call.message.chat.id,
                         text=f'Сообщение name={target_id}', reply_markup=None)
        bot.send_message(chat_id=call.message.chat.id,
                         text=f'Отправьте новый текст для name={target_id}',
                         reply_markup=kb_inl_admin.kb_edit_single_text_cancel())

        bot.register_next_step_handler(
            call.message, admin_edit_text, target_id)

    # ##### ------------------ Показать список текстов для редактирования
    if action == 'bot_texts_list':
        # Список текстов как при реплай кнопке
        text_editor.list_texts(call.message.chat)
        bot.send_message(
            call.message.chat.id, menu_msg('Параметры'),
            reply_markup=kb_params()
        )

    # ##### ------------------ Отменить подписку для пользователя
    if action == 'user_cancel_subscribe':
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
        pass
        # деактивировать старый

    #     установить новый тариф
    if action == 'deactivate_tariff':
        tariff_manager.deactivate_tariff(target_id)

        bot.send_message(chat_id=call.message.chat.id,
                         text=f'Тариф id {target_id} удален',
                         reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    # ##### ------------------ Добавить скидку тарифу
    if action == 'add_discount_tariff':
        bot.set_state(user_id, AdminTariffState.discount_percent, chat_id)
        # TODO - доавить получение id здесь
        set_state_data(bot, user_id, chat_id, {'discount_id': target_id})
        bot.send_message(
            chat_id, 'Введите размер скидки в процентах',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    # ##### ------------------ Выбрать продукт для нового тарифа
    if action == 'add_tariff_product':
        logger.info(f'-----> Действие ***{action}*** ')
        bot.set_state(user_id, AdminTariffState.type_product, chat_id)
        set_state_data(bot, user_id, chat_id, {'type_product': target_id})

        bot.edit_message_text(
            'Введите название нового тарифа (заголовок)', chat_id, mes_id,
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

        bot.set_state(user_id, AdminTariffState.name, chat_id)

    # ##### ------------------ Показать выбранные тарифы по продукту
    if action == 'tariffs_list_by_product':
        logger.info(f'-----> Действие ***{action}*** ')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=f'Список тарифов по продукту:', reply_markup=None)
        tariff_manager.admin_tariff_list_show(
            call.message, product_id=target_id)

        bot.send_message(call.message.chat.id,
                         text=f'Выполнение действий с тарифами', reply_markup=kb_inl_admin.kb_tariff_list())

    # ## Выбрать какое поле нужно редактировать в тарифе
    if action == 'edit_tariff':
        logger.info(f'-----> Действие ***{action}*** ')

        try:
            bot.set_state(user_id, AdminTariffState.choose_edit_field, chat_id)
            set_state_data(bot, user_id, chat_id, {'tariff_id': target_id})
        except Exception as e:
            print(f'Что то пошло не так {e}')
            # pass
            logger.error(f'Ошибка  [{e}]')

        change_text = 'Что хотите поменять?'
        text = tariff_manager.change_fields_tariff_show(target_id, change_text)
        bot.send_message(call.message.chat.id,
                         text=text,
                         reply_markup=kb_inl_admin.kb_change_tariff_fields(target_id))

    # ##### ------------------ Изменяем свойства тарифа
    if action == 'change_tariff_name':
        bot.set_state(user_id, AdminTariffState.edit_field_name, chat_id)
        set_state_data(bot, user_id, chat_id, {'tariff_id': target_id})
        bot.send_message(
            chat_id, 'Введите новое название тарифа',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    if action == 'change_tariff_duration':
        bot.set_state(user_id, AdminTariffState.edit_field_duration, chat_id)
        set_state_data(bot, user_id, chat_id, {'tariff_id': target_id})
        bot.send_message(
            chat_id, 'Введите новый период в днях',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    if action == 'change_tariff_description':
        bot.set_state(
            user_id, AdminTariffState.edit_field_description, chat_id)
        set_state_data(bot, user_id, chat_id, {'tariff_id': target_id})
        bot.send_message(
            chat_id, 'Введите новое описание',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    if action == 'change_tariff_price':
        bot.set_state(user_id, AdminTariffState.edit_field_price, chat_id)
        set_state_data(bot, user_id, chat_id, {'tariff_id': target_id})
        bot.send_message(
            chat_id, 'Введите новую стоимость',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    if action == 'change_tariff_image':
        bot.set_state(user_id, AdminTariffState.edit_field_image, chat_id)
        set_state_data(bot, user_id, chat_id, {'tariff_id': target_id})
        bot.send_message(
            chat_id, 'Отправьте новый постер (картинку)',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
