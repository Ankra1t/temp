from telebot import TeleBot
from telebot.types import CallbackQuery

from CALCULATE.callbacks import send_main
from MAIN.callbacks import send_user_education
from MAIN.callbacks.user.pages import send_user_account
from MAIN.common.utils import send_in_development

from initialize import tariff_manager, kb_inl_user

from .filter import user_main_factory, UserMainCallbackFilter


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = user_main_factory.parse(call.data)
    type = callback_data['type']

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'education':
        send_user_education(bot, call.message, user_id)

    if type == 'account':
        send_user_account(bot, call.message, user_id)

    if type == 'calculator':
        send_main(call.message, bot, user_id)

    if type == 'signals':
        send_in_development(bot, call.message)

    if type == 'buy':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=f'Какой продукт вас интересует?',
                              reply_markup=kb_inl_user.kb_select_products())
        # tariff_manager.tariff_list_show(call.message)


    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(UserMainCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        user_main=user_main_factory.filter())
