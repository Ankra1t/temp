from typing import Literal
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputMediaPhoto

from db import db
from data.data import liteDb
from service import user_settings_storage
from Classes import base_statis
from keyboards.admin_subs import kb_admin_subs
from models import Post, LANGUAGES_TYPE, Message, StateContext

from common.utils import delete_message, get_lang, get_print_float, get_print_signal_info
from common.dt import get_str_by_datetime

from messages.statistics import admin_main_statistics
from messages.admin import msg_admin_fut_posts, msg_admin_main, msg_admin_tariff, msg_admin_users, msg_admin_menu
from messages.common import POINT

from keyboards.admin_main import kb_admin_main, kb_admin_tools_list
from keyboards.admin_tariffs import kb_admin_tariffs, kb_admin_tariffs_back, kb_admin_tariffs_delete, kb_admin_tariffs_list, kb_admin_tariffs_edit
from keyboards.admin_users import kb_admin_client_info, kb_admin_users
from keyboards.admin_workers import kb_admin_workers, kb_admin_workers_actions, kb_admin_workers_support
from keyboards.admin_stats import kb_statistics
from keyboards.admin_posts import kb_posts
from keyboards.admin_params import kb_params


async def send_admin_main(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    count_all = db.get_users_count()
    count_admins = len(db.get_all_workes())

    count_blocked = len(db.get_blocked_users())
    count_with_sub = base_statis.count_payments_dry()

    todays_users = db.get_today_users()

    lang_counts: dict[LANGUAGES_TYPE, int] = {
        'ru': 0,
        'en': 0,
        'uz': 0,
        'tr': 0
    }
    for el in todays_users:
        lang = get_lang(el.get('tgId', -1))
        lang_counts[lang] += 1

    users = db.get_all_users()
    count_refs = 0
    for u in users:
        count_refs += 1 if u.refer_id else 0

    count_first_tries = count_first_lang = 0
    for el in todays_users:
        if liteDb.getFirstTryUser(el.get('tgId', -1)) == 1:
            count_first_tries += 1
        if liteDb.getFirstLang(el.get('tgId', -1)) == 1:
            count_first_lang += 1

    keyboard = kb_admin_main()
    text = msg_admin_main(
        count_all, count_with_sub, count_blocked,
        count_admins, len(todays_users), count_first_tries,
        count_first_lang, count_refs, lang_counts
    )

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_users(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    users = db.get_all_users()
    count_all = len(users)

    lang_counts: dict[LANGUAGES_TYPE, int] = {
        'ru': 0,
        'en': 0,
        'uz': 0,
        'tr': 0
    }
    for el in users:
        lang = get_lang(el.tg_id)
        lang_counts[lang] += 1

    count_blocked = len(db.get_blocked_users())
    count_with_sub = base_statis.count_payments_dry()

    text = msg_admin_users(count_all, count_with_sub,
                           count_blocked, lang_counts)
    keyboard = kb_admin_users()

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_payment(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    count_payments = base_statis.count_payments()
    summ_all_users = base_statis.summ_by_transactions()

    text = admin_main_statistics(count_payments, summ_all_users)
    keyboard = kb_statistics()

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_fut_posts(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    posts_count = len(db.get_all_posts())

    text = msg_admin_fut_posts(posts_count)
    keyboard = kb_posts()

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_params(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    text = msg_admin_menu('Параметры')
    keyboard = kb_params()

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_post(
    bot: AsyncTeleBot, chat_id: int, post: Post
):
    text = '\n'.join((
        '\n'.join((
            f'<b>{post.details.name}</b>' if post.details is not None else '',
            f'👉 {post.details.ticker}' if post.details is not None else '',
            '',
            get_print_signal_info(post.details.open_price,
                                  post.details.stop_loss),
            '',
        )) if post.details is not None else '',
        post.content,
        '',
        f'ID: <b>{post.id}</b>\n' if post.id is not None else ''
        f'Тип: <b>{"Рекомендация" if post.details is None else "Пост"}</b>',
        f'Дата и время поста: <b>{get_str_by_datetime(post.date_time)}</b>\n' if post.date_time is not None else ''
        f'Ограничение: <b>{post.direct}</b>',
    ))

    if post.mes_type == 'photo':
        await bot.send_photo(
            chat_id, post.media,
            caption=text
        )
    elif post.mes_type == 'video':
        await bot.send_video(
            chat_id, post.media,
            caption=text
        )
    else:
        await bot.send_message(chat_id, text)


async def send_admin_client(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    client_db_id: int,
    sort_by='',
    page=1,
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    client = db.get_user_by_id(client_db_id)
    if client is None:
        return

    user_subsribe = db.get_current_subscribe_user(client_db_id)

    fin_date = 'нет'
    type_subscribe_show = ''

    if user_subsribe is not None:
        fin_date = get_str_by_datetime(user_subsribe.finish_dt)
        type_subscribe_show = f' тип {user_subsribe.product_type}'

    sub_show = f'Подписка до: <b>{fin_date}</b> {type_subscribe_show}'

    nikname = f'@{client.tg_username}' if client.tg_username != '' else ''
    count_ref = len(db.get_user_referals(client_db_id))
    is_banned = client.ban

    block_show = ''
    if client.block:
        block_show = '🅱️ <b>Заблокировал бота</b>\n'

    ref_show = ''
    if client.refer_id is not None:
        ref_user = db.get_user_by_id(client.refer_id)
        if ref_user is not None:
            ref_show = f'Пришел от: <b>{f"@{ref_user.tg_username}" if ref_user.tg_username != "" else ref_user.id}</b>\n'

    calcs = db.get_calculations_by_user(client.id)
    calcs_count = len(calcs)

    calcs_info = f'Кол-во расчетов: <b>{calcs_count}</b>\n'
    for market in ('crypto', 'forex', 'RF', 'USA'):
        count = len([el for el in calcs if el.market == market])
        if count > 0:
            markets = {
                'crypto': 'Крипта',
                'forex': 'Форекс',
                'RF': 'РФ рынок',
                'USA': 'США рынок',
            }

            calcs_info += f'{POINT} {markets[market]}: <b>{count}</b>'

            u_base = user_settings_storage.get_or_create(client.tg_id)
            deposit = currency = risk = ''
            if u_base is not None:
                deposit = u_base.deposit or deposit
                currency = u_base.currency or currency

                if u_base.risk:
                    risk = ''.join((
                        f' Риск: <i>{u_base.risk[0]}',
                        ('%' if u_base.risk[1] else f'{currency}'),
                        '</i>'
                    ))

            if deposit != '' and currency != '':
                calcs_info += f' (Депозит: <u>{get_print_float(deposit)} {currency}</u>) {risk}'

            calcs_info += '\n'

    text = '\n'.join((
        f'Пользователь <b>{nikname} | {client_db_id} {"(BAN)" if is_banned else ""}</b>',
        sub_show,
        block_show,
        f'Рефералов: <b>{count_ref}</b>',
        ref_show,
        calcs_info,
        '<b>Выберите действие 👇</b>'
    ))
    keyboard = kb_admin_client_info(client_db_id, is_banned, page, sort_by)

    if is_first:
        await bot.send_message(
            chat_id, text,
            reply_markup=keyboard
        )
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_workers(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    text = msg_admin_menu('Работники')
    keyboard = kb_admin_workers()

    if is_first:
        await bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_workers_admin(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    res = '<b>Админы</b>\n'
    admins = db.get_admins()

    if len(admins) != 0:
        for i in range(0, len(admins)):
            res += f'\nID: {admins[i].id} | Username: @{admins[i].username}'
    else:
        res = '\nНет админов!'

    keyboard = kb_admin_workers_actions(1)

    if is_first:
        await bot.send_message(chat_id, res, reply_markup=keyboard)
    else:
        await bot.edit_message_text(
            res, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_workers_redactors(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    res = '<b>Редакторы</b>\n'
    redactors = db.get_redactors()

    if len(redactors) != 0:
        for i in range(0, len(redactors)):
            res += f'\nID: {redactors[i].id} | Username: @{redactors[i].username}'
    else:
        res = '\nНет редакторов!'

    keyboard = kb_admin_workers_actions(2)

    if is_first:
        await bot.send_message(chat_id, res, reply_markup=keyboard)
    else:
        await bot.edit_message_text(
            res, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_workers_support(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    sup = db.get_support_name()
    sup_link = f'@{sup}' if sup != '' else '-'

    text = f'Тех. поддержка: {sup_link}'
    keyboard = kb_admin_workers_support()

    if is_first:
        await bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_tariffs(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    await state.delete()

    text = msg_admin_menu('Тарифы')
    keyboard = kb_admin_tariffs()

    if is_first:
        await bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=keyboard
        )


async def send_admin_tariffs_list_item(
    bot: AsyncTeleBot,
    message: Message,
    page: int,
    type: Literal['default', 'delete', 'edit'] = 'default',
    is_first=False
):
    chat_id = message.chat.id
    mes_id = message.id

    tariffs = db.get_prices()
    count = len(tariffs)

    if count == 0:
        await bot.edit_message_text(
            'Тарифов нет', chat_id, mes_id,
            reply_markup=kb_admin_tariffs_back()
        )
    else:
        tariff = tariffs[page]

        text = msg_admin_tariff(tariff)
        image = tariff.img

        if type == 'delete':
            text += '\n\n⚠️<b>Удалить данный тарифы?</b>⚠️'
            keyboard = kb_admin_tariffs_delete(tariff.id or -1, page)
        elif type == 'edit':
            text += '\n\n<b>Что изменить?</b>'
            keyboard = kb_admin_tariffs_edit(tariff.id or -1, page)
        else:
            keyboard = kb_admin_tariffs_list(
                count, page, tariff.id or -1, tariff.switch_active == 1,
                tariff.discount is not None
            )

        async def send():
            if image is None:
                await bot.send_message(chat_id, text, reply_markup=keyboard)
            else:
                await bot.send_photo(
                    chat_id, image, text,
                    reply_markup=keyboard
                )

        if is_first:
            await send()
        elif message.content_type == 'photo' and image is not None:
            await bot.edit_message_media(
                InputMediaPhoto(image, text, 'HTML'), chat_id, mes_id,
                reply_markup=keyboard
            )
        elif message.content_type == 'text' and image is None:
            await bot.edit_message_text(
                text, chat_id, mes_id,
                reply_markup=keyboard
            )
        else:
            await delete_message(bot, chat_id, mes_id)
            await send()


async def send_admin_tools_list(
    bot: AsyncTeleBot,
    message: Message,
    turnover='',
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    turnover_show = ''
    if turnover:
        turnover_show = f'\nОборот от {turnover}M USDT'

    kb = kb_admin_tools_list(turnover)
    msg = f'Какие инструменты вы хотите получить?{turnover_show}'

    if is_first:
        await bot.send_message(
            chat_id, msg,
            reply_markup=kb
        )
    else:
        await bot.edit_message_text(
            msg,
            chat_id, mes_id,
            reply_markup=kb
        )


async def send_admin_subs(
    bot: AsyncTeleBot,
    message: Message,
    is_first=False,
):
    chat_id = message.chat.id
    mes_id = message.id

    kb = kb_admin_subs()
    msg = msg_admin_menu('Подписки')

    if is_first:
        await bot.send_message(
            chat_id, msg,
            reply_markup=kb
        )
    else:
        await bot.edit_message_text(
            msg,
            chat_id, mes_id,
            reply_markup=kb
        )
