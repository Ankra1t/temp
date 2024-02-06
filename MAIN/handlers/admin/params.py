import re
from telebot import TeleBot
from telebot.types import Message

from db import db
from db_new import db_new
from initialize import pay_guard

from common.utils import digit_accept, set_state_data, text_accept, get_normal_text
from MAIN.callbacks import kb_params_choice, kb_params_back
from MAIN.states import AdminParamsState


_pair_pattern = r'^[a-zA-Z]{3}/[a-zA-Z]{3}$'


def handle_other_text(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    set_state_data(
        bot, user_id, chat_id, {
            'text': get_normal_text(message)}
    )

    bot.send_message(
        chat_id, 'Применить изменения?',
        reply_markup=kb_params_choice('change'))


def handle_future_name(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    name = text_accept(message)
    if name is None:
        bot.send_message(
            chat_id, 'Введите буквенное обозначение тикера:',
            reply_markup=kb_params_back())
        return

    set_state_data(bot, user_id, chat_id, {'future_name': name})
    bot.set_state(user_id, AdminParamsState.future_step, chat_id)
    bot.send_message(
        chat_id, 'Введите шаг фьючерса:',
        reply_markup=kb_params_back())


def handle_future_step(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    step = digit_accept(message)
    if step is None:
        bot.send_message(
            chat_id, 'Введите число:',
            reply_markup=kb_params_back())
        return

    set_state_data(bot, user_id, chat_id, {'future_step': step})
    bot.set_state(user_id, AdminParamsState.future_price_step, chat_id)
    bot.send_message(
        chat_id, 'Введите цену шага фьючерса:',
        reply_markup=kb_params_back())


def handle_future_price_step(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    price_step = digit_accept(message)
    if price_step is None:
        bot.send_message(
            chat_id, 'Введите число:',
            reply_markup=kb_params_back())
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        name = data.get('future_name')
        step = int(data.get('future_step'))

    db_new.update_future(name, step, price_step)
    bot.delete_state(user_id, chat_id)
    bot.send_message(
        chat_id, 'Тикер успешно добавлен!\nВведите тикер фьючерса:',
        reply_markup=kb_params_back())
    bot.set_state(user_id, AdminParamsState.future_name, chat_id)


def handle_forex_pair(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    pair = text_accept(message)
    if pair is None or re.match(_pair_pattern, pair) is None:
        bot.send_message(
            chat_id, 'Введите пару в формате (XXX/XXX):',
            reply_markup=kb_params_back())
        return
    pair = pair.upper()

    set_state_data(bot, user_id, chat_id, {'pair': pair})
    bot.send_message(
        chat_id, 'Введите цену пары:',
        reply_markup=kb_params_back())
    bot.set_state(user_id, AdminParamsState.forex_price, chat_id)


def handle_forex_price(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    price = digit_accept(message)
    if price is None:
        bot.send_message(
            chat_id, 'Введите число:',
            reply_markup=kb_params_back())
        return

    set_state_data(bot, user_id, chat_id, {'price': price})
    bot.send_message(
        chat_id, 'Введите вспомогательную пару (XXX/XXX) или "-", если её нет:',
        reply_markup=kb_params_back())
    bot.set_state(user_id, AdminParamsState.forex_help_pair, chat_id)


def handle_forex_help_pair(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    help_pair = text_accept(message)
    if help_pair is None or not (help_pair == '-' or re.match(_pair_pattern, help_pair) is not None):
        bot.send_message(
            chat_id, 'Введите пару в формате (XXX/XXX) или "-":',
            reply_markup=kb_params_back())
        return
    help_pair = help_pair.upper() if help_pair != '-' else None

    with bot.retrieve_data(user_id, chat_id) as data:
        pair = data['pair']
        price = data['price']

    db.add_forex(pair, price, help_pair)
    bot.delete_state(user_id, chat_id)
    bot.send_message(
        chat_id, 'Пара успешно добавлен!\nВведите валютную пару:',
        reply_markup=kb_params_back())
    bot.set_state(user_id, AdminParamsState.forex_pair, chat_id)


def handle_count_trial_days(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    count_days = digit_accept(message, int)
    if count_days is None:
        bot.send_message(
            chat_id, 'Введите число:',
            reply_markup=kb_params_back())
        return

    # Сохраняем данные тарифа в таблице параметров
    pay_guard.set_option_trial_days(count_days)

    bot.send_message(
        chat_id, f'✅ Кол-во пробных дней {int(count_days)}дн. для нового пользователя сохранено',
        reply_markup=kb_params_back())

    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_other_text, state=AdminParamsState.text)

    reg_mes(handle_future_name, state=AdminParamsState.future_name)
    reg_mes(handle_future_step, state=AdminParamsState.future_step)
    reg_mes(handle_future_price_step, state=AdminParamsState.future_price_step)

    reg_mes(handle_forex_pair, state=AdminParamsState.forex_pair)
    reg_mes(handle_forex_price, state=AdminParamsState.forex_price)
    reg_mes(handle_forex_help_pair, state=AdminParamsState.forex_help_pair)

    reg_mes(handle_count_trial_days, state=AdminParamsState.count_trial_days)
