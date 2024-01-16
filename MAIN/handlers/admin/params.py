import re
from telebot import TeleBot
from telebot.types import Message

from db import db
from messages.workers import generate_normal_text
from common.utils import digit_accept, set_state_data, text_accept
from MAIN.callbacks import kb_params_choice, kb_params_back
from MAIN.states import AdminParamsState


_paire_pattern = r'^[a-zA-Z]{3}/[a-zA-Z]{3}$'


def handle_other_text(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    set_state_data(bot, user_id, chat_id, {
                   'text': generate_normal_text(message)})

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

    db.add_future(name, step, price_step)
    bot.delete_state(user_id, chat_id)
    bot.send_message(
        chat_id, 'Тикер успешно добавлен!\nВведите тикер фьючерса:',
        reply_markup=kb_params_back())
    bot.set_state(user_id, AdminParamsState.future_name, chat_id)


def handle_forex_paire(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    paire = text_accept(message)
    if paire is None or re.match(_paire_pattern, paire) is None:
        bot.send_message(
            chat_id, 'Введите пару в формате (XXX/XXX):',
            reply_markup=kb_params_back())
        return
    paire = paire.upper()

    set_state_data(bot, user_id, chat_id, {'paire': paire})
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
    bot.set_state(user_id, AdminParamsState.forex_help_paire, chat_id)


def handle_forex_help_paire(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    help_paire = text_accept(message)
    if help_paire is None or not (help_paire == '-' or re.match(_paire_pattern, help_paire) is not None):
        bot.send_message(
            chat_id, 'Введите пару в формате (XXX/XXX) или "-":',
            reply_markup=kb_params_back())
        return
    help_paire = help_paire.upper() if help_paire != '-' else None

    with bot.retrieve_data(user_id, chat_id) as data:
        paire = data['paire']
        price = data['price']

    db.add_forex(paire, price, help_paire)
    bot.delete_state(user_id, chat_id)
    bot.send_message(
        chat_id, 'Пара успешно добавлен!\nВведите валютную пару:',
        reply_markup=kb_params_back())
    bot.set_state(user_id, AdminParamsState.forex_paire, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_other_text, state=AdminParamsState.text)

    reg_mes(handle_future_name, state=AdminParamsState.future_name)
    reg_mes(handle_future_step, state=AdminParamsState.future_step)
    reg_mes(handle_future_price_step, state=AdminParamsState.future_price_step)

    reg_mes(handle_forex_paire, state=AdminParamsState.forex_paire)
    reg_mes(handle_forex_price, state=AdminParamsState.forex_price)
    reg_mes(handle_forex_help_paire, state=AdminParamsState.forex_help_paire)
