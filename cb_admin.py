from telebot import types
from datetime import datetime
from handlers.AdminHandler import admin_edit_text, get_start_date_cancel_subscribe, get_user_for_cancel_subscribe, update_support

from initialize import bot, db, kb_inl_admin, text_editor, pay_guard, tariff_manager
from messages.workers import admin_users_msg, admin_fut_posts_msg, menu_msg
import variables as vars

from messages.workers import admin_main_msg
from models import User

from common.utils import set_state_data
from MAIN.callbacks import (
    kb_admin_workers_actions, kb_params, kb_posts,
    kb_admin_users, kb_admin_users_back
)
from MAIN.states import AdminTariffState

from cb_filters import (admin_default_factory, adm_action, admin_main_factory,
                        admin_workerss_factory)
from config_logger import logger


@bot.callback_query_handler(func=None, admin_main=admin_main_factory.filter())
def admin_main_callbacks(call: types.CallbackQuery):
    callback_data: dict = admin_main_factory.parse(call.data)
    type = callback_data['type']
    logger.info(f'Кастомное callback_query меню ***{type}***')

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'users':
        logger.info(f'-----> Нажали меню пользователи ')
        count_all = db.get_users_count()
        count_with_sub = pay_guard.get_paid_users()
        count_old = pay_guard.get_paid_more1_users()
        text = admin_users_msg(count_all, len(count_with_sub), len(count_old))

        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_admin_users()
        )

    if type == 'workers':
        bot.edit_message_text(
            menu_msg('Работники'), chat_id, mes_id,
            reply_markup=kb_inl_admin.workers(),
            parse_mode='HTML')

    if type == 'fut_posts':
        bot.edit_message_text(
            admin_fut_posts_msg(), chat_id, mes_id,
            reply_markup=kb_posts()
        )

    if type == 'tariffs':
        bot.edit_message_text('Действия с тарифами', chat_id, mes_id,
                              reply_markup=kb_inl_admin.kb_tariffs())

    if type == 'params':
        bot.edit_message_text(menu_msg('Параметры'), chat_id, mes_id,
                              reply_markup=kb_params(),
                              parse_mode='HTML')

    bot.clear_step_handler(call.message)
    bot.delete_state(user_id, chat_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=None, adminn_workerss=admin_workerss_factory.filter())
def admin_workers_callbacks(call: types.CallbackQuery):
    callback_data: dict = admin_workerss_factory.parse(call.data)
    type = callback_data['type']
    logger.info(f'Кастомное callback_query меню ***{type}***')

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'admins':
        bot.edit_message_text(menu_msg('Главные админы'), chat_id, mes_id,
                              reply_markup=kb_admin_workers_actions('admin'),
                              parse_mode='HTML')

    if type == 'redactors':
        bot.edit_message_text(menu_msg('Редакторы'), chat_id, mes_id,
                              reply_markup=kb_admin_workers_actions(
                                  'redactor'),
                              parse_mode='HTML')

    if type == 'support':
        sup = db.get_support()
        bot.edit_message_text(f'Тех.поддержка: {sup[0][2]}', chat_id, mes_id,
                              reply_markup=kb_inl_admin.workers_support())

    if type == 'workers_list':
        mas = db.get_all_workes()
        res = ''
        role = ''
        for i in range(0, len(mas)):
            if mas[i][2] == 1:
                role = 'Гл.админ'
            if mas[i][2] == 2:
                role = 'Редактор'
            if mas[i][2] == 3:
                role = 'Тех.поддержка'
            res += '\n' + str(mas[i][0]) + ' | ' + \
                mas[i][1] + '\nДолжность: ' + role + '\n'
        bot.edit_message_text(res, chat_id, mes_id,
                              reply_markup=kb_inl_admin.workers())

    bot.clear_step_handler(call.message)
    bot.delete_state(user_id, chat_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=None, admin_default=admin_default_factory.filter())
def admin_default_callbacks(call: types.CallbackQuery):
    callback_data: dict[str, str] = admin_default_factory.parse(call.data)
    type = callback_data['type']
    logger.info(f'Кастомное callback_query меню ***{type}***')

    chat_id = call.message.chat.id
    mes_id = call.message.id
    user_id = call.from_user.id

    if 'update_support' in type and type != 'update_support':
        if 'yes' in type:
            vars.sup_name = vars.sup_name.replace('@', '')
            db.update_sup(vars.sup_name)
            bot.edit_message_text('Изменено!', chat_id, mes_id)
        if 'no' in type:
            vars.sup_name = ''

        sup = db.get_support()
        bot.send_message(
            chat_id, f'Тех.поддержка: {sup[0][2]}', reply_markup=kb_inl_admin.workers_support())

    if type == 'update_support':
        bot.edit_message_text('Отправьте ник ТГ для тех. поддержки с @',
                              chat_id, mes_id,
                              reply_markup=kb_inl_admin.workers_actions_back('support'))
        bot.register_next_step_handler(
            call.message, update_support)

    # ## Главное меню
    if type == 'go_main':
        logger.info(f'-----> Выбрано меню ***{type}*** ')
        try:
            count_all = db.get_users_count()
            count_with_sub = len(db.get_users_with_sub())
            count_old = len(db.get_users_with_more_pay())
            count_admins = len(db.get_all_workes())
            count_fut_posts = len(db.get_fut_all_posts())
            text = admin_main_msg(count_all, count_with_sub,
                                  count_old, count_admins, count_fut_posts)

            bot.edit_message_text(text, chat_id, mes_id,
                                  reply_markup=kb_inl_admin.main(), parse_mode='HTML')

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
    if type == 'add_tariff':
        logger.info(f'-----> Выбрано меню ***{type}*** ')

        bot.edit_message_text(
            'Введите название нового тарифа (заголовок)', chat_id, mes_id,
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

        bot.set_state(user_id, AdminTariffState.name, chat_id)

    # ## Показать список тарифов
    if type == 'tariffs_list':
        logger.info(f'-----> Выбрано меню ***{type}*** ')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=f'Список добавленных тарифов', reply_markup=None)
        tariff_manager.admin_tariff_list_show(call.message)

        bot.send_message(call.message.chat.id,
                         text=f'Выполнение действий с тарифами', reply_markup=kb_inl_admin.kb_tariff_list())

    # ## Показать список действующих скидок
    if type == 'discount_list_active':
        logger.info(f'-----> Выбрано меню ***{type}*** ')
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
        #                       text=f'--- Список действующих скидок:', reply_markup=None)

        bot.send_message(call.message.chat.id,
                         text=f'--- Список действующих скидок:', reply_markup=None)
        tariff_manager.admin_discount_list(call.message, type_discount='active')

        bot.send_message(call.message.chat.id,
                         text=f'Выполнение действий с тарифами', reply_markup=kb_inl_admin.kb_tariff_list())

    # ## Показать список Прошедших скидок
    if type == 'discount_list_inactive':
        logger.info(f'-----> Выбрано меню ***{type}*** ')
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
        #                       text=f'--- Список прошедших скидок:', reply_markup=None)
        bot.send_message(call.message.chat.id,
                         text=f'--- Список прошедших скидок:', reply_markup=None)
        tariff_manager.admin_discount_list(call.message, type_discount='inactive')

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
    user_id = call.from_user.id

    # ##### ------------------ Редактируем сообщения из БД
    if action == 'edit_bot_text':
        logger.info(f'-----> Действие ***{action}*** ')

        # Спрятать reply клаву
        bot.send_message(chat_id=call.message.chat.id,
                         text=f'Сообщение id={target_id}', reply_markup=None)
        bot.send_message(chat_id=call.message.chat.id,
                         text=f'Отправьте новый текст для id={target_id}',
                         reply_markup=kb_inl_admin.kb_edit_single_text_cancel())

        bot.register_next_step_handler(
            call.message, admin_edit_text, target_id)

    # ##### ------------------ Показать список текстов для редактирования
    if action == 'bot_texts_list':
        # Список текстов как при реплай кнопке
        text_editor.list_texts(call.message.chat)
        bot.send_message(call.message.chat.id, menu_msg('Параметры'),
                         reply_markup=kb_params(), parse_mode='HTML')

    # ##### ------------------ Разбанить пользователя по id
    if action == 'unban_user':
        # Убираем из бана
        pay_guard.unban_user_by_id(target_id)
        user = vars.user_dict[call.message.chat.id]
        bot.send_message(chat_id=call.message.chat.id,
                         text=f'Пользователь {user.username} id {user.id} разбанен и имеет полные клиентские права',
                         reply_markup=kb_inl_admin.kb_success_ban_actions())

        # Сбросить обработчик приема username для бана
        bot.clear_step_handler(call.message)

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
        bot.set_state(user_id, AdminTariffState.edit_field_description, chat_id)
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