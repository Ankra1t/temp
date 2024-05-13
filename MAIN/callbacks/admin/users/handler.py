import math
from telebot import TeleBot
from telebot.types import CallbackQuery

from MAIN.common.messages import msg_admin_users_markets
from MAIN.common.utils import get_short_user_info
from MAIN.states import AdminUsersState
from common.dt import get_str_by_datetime
from common.utils import set_state_data

from config_logger import logger

from Classes import pay_guard
from db import SORT_BY_TYPE, db
from messages.users import gift_subscribe_msg


from .keyboards import (
    kb_admin_choose_list, kb_admin_users_back, kb_admin_users_cancel,
    kb_admin_users_confirm, kb_admin_client_list, kb_admin_users_markets
)
from .filter import admin_users_factory, AdminUsersCallbackFilter
from ..pages import send_admin_client, send_admin_main, send_admin_users


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data = admin_users_factory.parse(call.data)

    type: str = callback_data.get('type', '')
    sort_by: SORT_BY_TYPE = callback_data.get(
        'sort_by', 'new'
    )  # type: ignore
    filter: str = callback_data.get('filter', '')
    client_db_id = int(callback_data.get('client_db_id', 0))
    page = int(callback_data.get('page', 1))

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'go_main':
        send_admin_main(bot, call.message, user_id)

    if type == 'go_users':
        send_admin_users(bot, call.message, user_id)

    if type == 'lists':
        bot.edit_message_text(
            'Выберите <u>список</u> клиентов', chat_id, mes_id,
            reply_markup=kb_admin_choose_list()
        )

    if type == 'client_list':
        if filter == '':
            # Значения для постраничного вывода
            limit = 6
            users_count = db.get_users_count()
            pages_count = math.ceil(users_count / limit)

            users = db.get_paginated_users(
                limit, page, sort_by
            )

            text = '<b>Все клиенты</b>\n'

            if len(users) == 0:
                text += '\nНет пользователей'
            else:
                text += '<b>ID | Тг данные | Остаток расчетов</b>\n'
                for user in users:
                    text += '\n' + get_short_user_info(user) + '\n'

                sort_by_text = 'новым' if (sort_by == 'new') else 'старым'
                text += f'\n     | Сортировка по <b>{sort_by_text}</b> |'

            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb_admin_client_list(
                    pages_count, page, sort_by, filter
                )
            )

        if filter == 'ban':
            limit = 10
            users_count = len(db.get_banned_users())
            pages_count = math.ceil(users_count / limit)

            users = db.get_banned_users(limit, page, sort_by)
            text = '⛔️  <b>Забаненные</b>\n'

            if len(users) == 0:
                text += '\nНет пользователей'
            else:
                for user in users:
                    nik = f'@{user.tg_username}' if (
                        user.tg_username is not None) else 'Скрыт'
                    ban = '(BAN)' if user.ban == 1 else ''

                    text += f'\n{ban} {user.tg_id} | {nik}\n'

            bot.edit_message_text(
                text,
                chat_id, mes_id,
                reply_markup=kb_admin_client_list(
                    pages_count, page, sort_by, filter
                )
            )

        if filter == 'paid':
            users = db.get_subsribed_users()

            text = '💵 <b>Платные</b>\n'
            if len(users) == 0:
                text += '\nНет пользователей'
            else:
                for user in users:
                    text += '\n' + get_short_user_info(user) + '\n'

            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb_admin_users_cancel(sort_by, page, filter)
            )

        if filter == 'new':
            users = db.get_paginated_users(10, 1, 'new')

            text = '<b>Новые пользователи</b>\n'

            if len(users) == 0:
                text += '\nНет пользователей'
            else:
                for user in users:
                    text += '\n' + get_short_user_info(user) + '\n'

            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb_admin_users_cancel(sort_by, page, filter)
            )

    if type == 'client_add_sub':
        # Задать сначала тариф для выдачи подписки
        bot.set_state(user_id, AdminUsersState.subscribe_days, chat_id)
        set_state_data(bot, user_id, chat_id, {
            'user_id': client_db_id,
        })
        bot.edit_message_text(
            'Выберите тариф на базе которого выдать подписку:',
            chat_id, mes_id,
            reply_markup=kb_admin_users_back()
        )

    if type == 'choose_periods_for_tariffs':
        with bot.retrieve_data(user_id, chat_id) as data:
            tariff_id = data.get('tariff_id')
            subscribe_user_id = data.get('user_id')

        # Получить tg_user_id
        user = db.get_user_by_id(subscribe_user_id)

        if user is None:
            logger.error(
                f'[choose_periods_for_tariffs]: user_id={subscribe_user_id}'
            )
            return

        # Считаем кол-во дней для выдачи по периоду
        days = pay_guard.get_days_by_period(sort_by)

        tariff = db.get_price_by_id(tariff_id)
        if tariff is None:
            logger.error(f'[choose_periods_for_tariffs]: tariff_id={tariff_id}')
            return

        pay_guard.set_subscribe_unactive_by_user_id(user.tg_id)
        datetime_show = pay_guard.set_trial(
            user.tg_id, tariff.type_product, int(days)
        )

        data_fin = get_str_by_datetime(datetime_show)
        bot.send_message(
            chat_id,
            f'Клиенту с id[{subscribe_user_id}] установлена платная подписка до {data_fin}'
        )

        bot.delete_state(user_id, chat_id)

        send_admin_client(bot, call.message, user_id, subscribe_user_id, True)

        bot.send_message(
            user.tg_id, gift_subscribe_msg(user.tg_id, data_fin)
        )

    if type == 'client_cancel_sub':
        bot.edit_message_text(
            f'Отменить все подписки пользователю с id[{client_db_id}?]',
            chat_id, mes_id,
            reply_markup=kb_admin_users_confirm('cancel_sub', client_db_id)
        )

    if type == 'client_ban':
        user = db.get_user_by_id(client_db_id)
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
        user = db.get_user_by_id(client_db_id)
        if user is None:
            return

        if 'cancel_sub' in type:
            pay_guard.set_subscribe_unactive_by_user_id(user.tg_id)
        if 'ban' in type:
            db.set_user_ban(user.id, abs(user.ban - 1))

        bot.edit_message_text('Успешно!', chat_id, mes_id)

    if 'confirm_no' in type:
        bot.edit_message_text('Отменено!', chat_id, mes_id)

    if 'confirm' in type:
        send_admin_client(
            bot, call.message,
            user_id, client_db_id,
            True, sort_by, page
        )

    if type == 'client_search':
        bot.edit_message_text(
            'Введите id или имя пользователя:',
            chat_id, mes_id,
            reply_markup=kb_admin_users_cancel(sort_by, page)
        )
        bot.set_state(user_id, AdminUsersState.client_search, chat_id)
        set_state_data(bot, user_id, chat_id, {
            'sort_by': sort_by,
            'page': page
        })

    if type == 'client_set_trial_custom':
        bot.set_state(
            user_id, AdminUsersState.trial_subscribe_days_get_days, chat_id)
        logger.error(f'Назначить пробную подписку пользователю handler')
        set_state_data(bot, user_id, chat_id, {
            'user_id': client_db_id,
        })
        bot.edit_message_text(
            'Введите количество дней ПРОБНОЙ подписки:',
            chat_id, mes_id,
            reply_markup=kb_admin_users_back()
        )

    if type == 'markets':
        users_markets_count = db.get_users_each_market_count()

        if filter == '':
            bot.edit_message_text(
                msg_admin_users_markets(users_markets_count), chat_id, mes_id,
                reply_markup=kb_admin_users_markets()
            )
        else:
            limit = 6
            users_count = users_markets_count.get(filter, 0)
            pages_count = math.ceil(users_count / limit)

            users = db.get_paginated_users(
                limit, page, sort_by, filter # type: ignore
            )

            if filter == 'crypto':
                market_text = 'крипте'
            elif filter == 'forex':
                market_text = 'форекс'
            elif filter == 'RF':
                market_text = 'рынке РФ'
            else:
                market_text = 'рынке США'

            text = f'<b>Клиенты в {market_text}</b>\n'

            if len(users) == 0:
                text += '\nНет пользователей'
            else:
                text += '<b>ID | Тг данные | Остаток расчетов</b>\n'
                for user in users:
                    text += '\n' + get_short_user_info(user) + '\n'

                sort_by_text = 'новым' if (sort_by == 'new') else 'старым'
                text += f'\n     | Сортировка по <b>{sort_by_text}</b> |'

            bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=kb_admin_client_list(
                    pages_count, page, sort_by, filter, 'markets'
                )
            )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminUsersCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_users=admin_users_factory.filter())
