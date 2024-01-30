import math
from telebot import TeleBot
from telebot.types import CallbackQuery
from common.utils import set_state_data
from common.vars import PRINT_DATE_FROMAT

from initialize import kb_inl_admin, pay_guard
from db_new import db_new
from models import User
from MAIN.states import AdminUsersState

from .keyboards import kb_admin_users_back, kb_admin_users_cancel, kb_admin_users_confirm, kb_admin_users_list
from .filter import admin_users_factory, AdminUsersCallbackFilter
from ..pages import send_admin_client


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = admin_users_factory.parse(call.data)

    type: str = callback_data.get('type') or ''
    filter: str = callback_data.get('filter') or ''
    client_db_id = int(callback_data.get('client_db_id') or 0)
    page = int(callback_data.get('page') or 1)

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'cancel_subscribe':
        bot.edit_message_text(
            'Отменить подписку', chat_id, mes_id,
            reply_markup=kb_inl_admin.users_cancel_subscribe()
        )

    if type == 'ban_list':
        limit = 10
        users = db_new.get_banned_users()
        count = len(users)

        pages = math.ceil(count / limit)

        users = users[(page - 1) * limit:page * limit]
        text = ''

        if len(users) == 0:
            text = 'Нет забаненных пользователей'
        else:
            for user in users:
                nik = f'@{user.username}' if (
                    user.username is not None) else 'Скрыт'
                ban = '(BAN)' if user.ban == 1 else ''

                text += f'\n{ban} {user.tg_id} | {nik}\n'

        bot.edit_message_text(
            text,
            chat_id, mes_id,
            reply_markup=kb_admin_users_list(pages, page, filter, False)
        )

    if type == 'client_list':
        limit = 6
        count = db_new.get_users_count()

        pages = math.ceil(count / limit)

        mas_all_user = db_new.get_paginated_users(
            limit, page,
            'by_date_old' if filter == 'by_date_old' else ''
        )
        text = ''

        if len(mas_all_user) == 0:
            text = 'Нет пользователей'
        else:
            for user in mas_all_user:
                tg_user_id = user.tg_id

                nik = f'@{user.username}' if user.username != '' else 'Скрыт'
                ban = '(BAN)' if user.ban == 1 else ''

                user_subsriber = User()
                user_subsriber.id = tg_user_id
                user_subsriber = pay_guard.get_current_subscribe_user(
                    user_subsriber)

                fin_date = 'нет подписок'
                type_subscribe_show = ''

                if user_subsriber.subscribe is not None:
                    fin_date = user_subsriber.subscribe.finish_dt.strftime(
                        '%d/%m/%Y')
                    type_subscribe_show = f' тип {user_subsriber.subscribe.type}'

                user_show = (
                    f'\n{user.id} | {nik} {ban}'
                    f'\nПодписка до: {fin_date}<b>{type_subscribe_show}</b>'
                    f'\nЗарегестрирован <b>{user.registration_dt.strftime(PRINT_DATE_FROMAT)}</b>\n'
                )

                if (user_subsriber.subscribe is not None) and (filter == 'by_paid'):
                    text = user_show + text
                else:
                    text += user_show

        bot.edit_message_text(
            text or 'Нет пользователей', chat_id, mes_id,
            reply_markup=kb_admin_users_list(pages, page, filter)
        )

    if type == 'client_add_sub':
        bot.set_state(user_id, AdminUsersState.subscribe_days, chat_id)
        set_state_data(bot, user_id, chat_id, {
            'user_id': client_db_id,
        })
        bot.edit_message_text(
            'Введите количество дней подписки:',
            chat_id, mes_id,
            reply_markup=kb_admin_users_back()
        )

    if type == 'client_cancel_sub':
        bot.edit_message_text(
            f'Отменить подписку пользователю с id[{client_db_id}?]',
            chat_id, mes_id,
            reply_markup=kb_admin_users_confirm('cancel_sub', client_db_id)
        )

    if type == 'client_ban':
        user = db_new.get_user_by_id(client_db_id)
        if user is None:
            return
        is_banned = user.ban == 1

        if is_banned:
            text = f'Разбанить пользователя с id[{client_db_id}]'
        else:
            text = f'Забанить пользователя с id[{client_db_id}]'

        bot.edit_message_text(
            text,
            chat_id, mes_id,
            reply_markup=kb_admin_users_confirm('ban', client_db_id)
        )

    if 'confirm_yes' in type:
        user = db_new.get_user_by_id(client_db_id)
        if user is None:
            return

        if 'cancel_sub' in type:
            pay_guard.set_subscribe_unactive_by_user_id(client_db_id)
        if 'ban' in type:
            db_new.set_user_ban(user.id, abs(user.ban - 1))

        bot.edit_message_text('Успешно!', chat_id, mes_id)

    if 'confirm_no' in type:
        bot.edit_message_text('Отменено!', chat_id, mes_id)

    if type == 'client_search':
        bot.edit_message_text(
            'Введите id или имя пользователя:',
            chat_id, mes_id,
            reply_markup=kb_admin_users_cancel(filter, page)
        )
        bot.set_state(user_id, AdminUsersState.client_search, chat_id)
        set_state_data(bot, user_id, chat_id, {
            'filter': filter,
            'page': page
        })

    if 'confirm' in type:
        send_admin_client(
            bot, call.message,
            user_id, client_db_id,
            True, filter, page
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminUsersCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_users=admin_users_factory.filter())
