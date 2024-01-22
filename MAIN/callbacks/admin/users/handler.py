from datetime import datetime
import math
from telebot import TeleBot
from telebot.types import CallbackQuery

from initialize import kb_inl_admin, pay_guard
from db import db
from models import User
from MAIN.states import AdminUsersState

from .keyboards import kb_admin_users_back, kb_admin_users_list
from .filter import admin_users_factory, AdminUsersCallbackFilter


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = admin_users_factory.parse(call.data)
    type = callback_data['type']

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'put_subscribe':
        bot.edit_message_text('Отправьте ник клиента', chat_id, mes_id,
                              reply_markup=kb_admin_users_back())

        bot.set_state(user_id, AdminUsersState.subscribe_username, chat_id)

    if type == 'add_sub_subscribe':
        bot.edit_message_text('Отправьте id клиента', chat_id, mes_id,
                              reply_markup=kb_admin_users_back())

        bot.set_state(user_id, AdminUsersState.sub_user_id, chat_id)

    if type == 'cancel_subscribe':
        bot.edit_message_text(
            'Отменить подписку', chat_id, mes_id,
            reply_markup=kb_inl_admin.users_cancel_subscribe()
        )

    if type == 'ban_list':
        users = pay_guard.get_ban_users()

        for user in users:
            tg_user_id = str(user[9])
            nik = str(user[2]) if user[2] else 'Скрыт'
            ban = ' (BAN) ' if user[10] is not None else ''

            user_info = f'\n {ban} {tg_user_id} | {nik} '
            bot.send_message(chat_id, user_info,
                             reply_markup=kb_inl_admin.user_unbun(tg_user_id))

        bot.send_message(chat_id, 'Отправьте username для бана пользователя:',
                         reply_markup=kb_admin_users_back())

        bot.set_state(user_id, AdminUsersState.ban_username, chat_id)

    if 'client_list' in type:
        type_list = type.split('+')

        page = int(type_list[1]) if len(type_list) == 2 else 1

        limit = 10
        count = db.get_users_count()

        pages = math.ceil(count / limit)

        mas_all_user = db.get_all_users(limit, page)
        res_str_all_users = ''

        for user in mas_all_user:
            tg_user_id = int(user[9])
            nik = f'@{user[2]}' if user[2] else 'Скрыт'
            ban = ' (BAN) ' if user[10] is not None else ''
            user = User()
            user.id = tg_user_id
            user_subsriber = pay_guard.get_current_subscribe_user(user)

            fin_date = 'нет подписок'
            type_subscribe_show = ''
            if user_subsriber.subscribe is not None:
                fin_date = user_subsriber.subscribe.finish_dt
                fin_date = fin_date.strftime('%d/%m/%Y')
                type_subscribe = user_subsriber.subscribe.type
                type_subscribe_show = f' тип {type_subscribe}'

            res_str_all_users += (f'\n {ban}{str(tg_user_id)} | {nik}   '
                                  f'\nПодписка (окончание): {fin_date}{type_subscribe_show}\n')

        kb = kb_admin_users_list(pages, page) if (
            pages > limit) else kb_admin_users_back()

        bot.edit_message_text(
            res_str_all_users, chat_id, mes_id,
            reply_markup=kb
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminUsersCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_users=admin_users_factory.filter())
