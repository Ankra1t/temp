import re
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from db import db
from Classes import pay_guard

from common.utils import digit_accept, set_state_data, text_accept, get_normal_text

from states.admin_params import AdminParamsState
from keyboards.admin_params import kb_params_choice, kb_params_back


_pair_pattern = r'^[a-zA-Z]{3}/[a-zA-Z]{3}$'


async def handle_other_text(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    await set_state_data(
        bot, user_id, chat_id, {
            'text': get_normal_text(message)
        }
    )

    await bot.send_message(
        chat_id, 'Применить изменения?',
        reply_markup=kb_params_choice('change')
    )


async def handle_forex_pair(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    pair = text_accept(message)
    if pair is None or re.match(_pair_pattern, pair) is None:
        await bot.send_message(
            chat_id, 'Введите пару в формате (XXX/XXX):',
            reply_markup=kb_params_back())
        return
    pair = pair.upper()

    await set_state_data(bot, user_id, chat_id, {'pair': pair})
    await bot.send_message(
        chat_id, 'Введите цену пары:',
        reply_markup=kb_params_back())
    await bot.set_state(user_id, AdminParamsState.forex_price, chat_id)


async def handle_forex_price(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    price = digit_accept(message)
    if price is None:
        await bot.send_message(
            chat_id, 'Введите число:',
            reply_markup=kb_params_back())
        return

    await set_state_data(bot, user_id, chat_id, {'price': price})
    await bot.send_message(
        chat_id, 'Введите вспомогательную пару (XXX/XXX) или "-", если её нет:',
        reply_markup=kb_params_back())
    await bot.set_state(user_id, AdminParamsState.forex_help_pair, chat_id)


async def handle_forex_help_pair(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    help_pair = text_accept(message)
    if help_pair is None or not (help_pair == '-' or re.match(_pair_pattern, help_pair) is not None):
        await bot.send_message(
            chat_id, 'Введите пару в формате (XXX/XXX) или "-":',
            reply_markup=kb_params_back())
        return
    help_pair = help_pair.upper() if help_pair != '-' else None

    async with bot.retrieve_data(user_id, chat_id) as data:
        pair = data.get('pair', '')
        price = data.get('price', 0)

    db.update_forex(pair, price, help_pair)
    await bot.delete_state(user_id, chat_id)
    await bot.send_message(
        chat_id, 'Пара успешно добавлен!\nВведите валютную пару:',
        reply_markup=kb_params_back())
    await bot.set_state(user_id, AdminParamsState.forex_pair, chat_id)


async def handle_count_trial_days(message: Message, bot: AsyncTeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    count_days = digit_accept(message, int)
    if count_days is None:
        await bot.send_message(
            chat_id, 'Введите число:',
            reply_markup=kb_params_back())
        return

    # Сохраняем данные тарифа в таблице параметров
    pay_guard.set_option_trial_days(count_days)

    await bot.send_message(
        chat_id, f'✅ Кол-во пробных дней {int(count_days)}дн. для нового пользователя сохранено',
        reply_markup=kb_params_back()
    )

    await bot.delete_state(user_id, chat_id)


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_other_text, state=AdminParamsState.text)

    reg_mes(handle_forex_pair, state=AdminParamsState.forex_pair)
    reg_mes(handle_forex_price, state=AdminParamsState.forex_price)
    reg_mes(handle_forex_help_pair, state=AdminParamsState.forex_help_pair)

    reg_mes(handle_count_trial_days, state=AdminParamsState.count_trial_days)
