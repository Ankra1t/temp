from telebot import TeleBot
from telebot.types import CallbackQuery

from db import db

from .keyboards import kb_user_referral, kb_user_referral_list
from .filter import user_account_factory, UserAccountCallbackFilter

from MAIN.states import UserAccountState
from MAIN.callbacks import send_user_account, send_user_main
from MAIN.common.utils import send_in_development
from MAIN.common.messages import msg_referral


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = user_account_factory.parse(call.data)
    type = callback_data.get('type') or ''

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id
    
    # цена входа
    # 

    if type == 'purchases' or type == 'buy_month':
        send_in_development(bot, call.message)

    if type == 'main':
        send_user_main(bot, call.message, user_id)

    if type == 'back':
        send_user_account(bot, call.message, user_id)

    if type == 'referral':
        referals = db.get_referals(user_id)
        count_ref = len(referals)
        intext = msg_referral(count_ref)
        bot.send_message(
            chat_id, text=intext, parse_mode="HTML",
            reply_markup=kb_user_referral()
        )

    if type == 'referral_list':
        referals = db.get_referals(user_id)
        res = ''
        if len(referals) != 0:
            for i in range(0, len(referals)):
                res += f'\nНик: {referals[i][1]}\nВсего потратил: {referals[i][5]}'
        else:
            res = "К сожалению, у вас нет рефералов 😔\n<b>Отправьте</b> свой реферальную ссылку друзьями, чтобы это исправить 😉"
        bot.send_message(
            chat_id, res, reply_markup=kb_user_referral_list(), parse_mode="HTML")

    if type == 'password':
        bot.edit_message_text(
            'Введите новый пароль:', chat_id, mes_id
        )
        bot.set_state(user_id, UserAccountState.password, chat_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(UserAccountCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        user_account=user_account_factory.filter())
