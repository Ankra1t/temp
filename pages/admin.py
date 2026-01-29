from telebot.async_telebot import AsyncTeleBot

from models import Post, LANGUAGES_TYPE, Message, StateContext

from common.utils import get_lang, get_print_signal_info
from common.dt import get_str_by_datetime

from messages.admin import msg_admin_main, msg_admin_users, msg_admin_menu

from keyboards.admin_main import kb_admin_main, kb_admin_tools_list
from keyboards.admin_users import kb_admin_users
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

    # TODO: Получить статистику из API
    # count_all = db.get_users_count()
    # count_admins = len(db.get_all_workes())
    # count_blocked = len(db.get_blocked_users())
    # count_with_sub = base_statis.count_payments_dry()
    # todays_users = db.get_today_users()
    # users = db.get_all_users()

    # Временно используем заглушки
    count_all = 0
    count_admins = 0
    count_blocked = 0
    count_with_sub = 0
    count_refs = 0

    lang_counts: dict[LANGUAGES_TYPE, int] = {
        'ru': 0,
        'en': 0,
        'uz': 0,
        'tr': 0
    }

    count_first_tries = count_first_lang = 0
    # for el in todays_users:
    #     if liteDb.getFirstTryUser(el.get('tgId', -1)) == 1:
    #         count_first_tries += 1
    #     if liteDb.getFirstLang(el.get('tgId', -1)) == 1:
    #         count_first_lang += 1

    keyboard = kb_admin_main()
    text = msg_admin_main(
        count_all, count_with_sub, count_blocked,
        count_admins, 0, count_first_tries,
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

    # TODO: Получить пользователей из API
    users = []  # db.get_all_users()
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

    # TODO: Получить данные из API
    count_blocked = 0  # len(db.get_blocked_users())
    count_with_sub = 0  # base_statis.count_payments_dry()

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


# Убрано (оплата)
async def send_admin_payment(
    bot: AsyncTeleBot,
    message: Message,
    state: StateContext,
    is_first=False
):
    chat_id = message.chat.id

    await state.delete()
    await bot.send_message(chat_id, 'Статистика оплат недоступна')


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

    # TODO: Получить данные клиента из API
    # client = db.get_user_by_id(client_db_id)
    # if client is None:
    #     return

    # Временно показываем сообщение
    await bot.send_message(chat_id, 'Функция просмотра клиента временно недоступна')


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

    msg = msg_admin_menu('Подписки')

    if is_first:
        await bot.send_message(
            chat_id, msg,
        )
    else:
        await bot.edit_message_text(
            msg,
            chat_id, mes_id,
        )
