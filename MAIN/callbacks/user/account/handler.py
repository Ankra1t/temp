import asyncio
from pytonconnect import TonConnect
from telebot import TeleBot
from telebot.types import CallbackQuery

from Classes.TonWallet import get_connector
from config_logger import logger
from db import LANGUAGES, db

from .keyboards import (
    kb_params_choose_lang, kb_support, kb_user_params_back, kb_user_purchases,
    kb_user_referral, kb_user_referral_list, kb_params_choose_lang, kb_wallet_connect, kb_wallets
)
from .filter import user_account_factory, UserAccountCallbackFilter
from ..pages import send_referral, send_user_account, send_user_main, send_user_params

from MAIN.states import UserAccountState
from MAIN.common.messages import msg_enter_nickname, msg_referral, msg_referral_list, msg_user_purchases

from CALCULATE.common.messages import msg_choose_lang, msg_support


connector = get_connector(6919899538)

def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = user_account_factory.parse(call.data)
    type = callback_data.get('type') or ''

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    logger.info(
        f'callback "user_account_factory" user_tg_id={user_id} type={type}'
    )

    if type == 'purchases':
        purchases = db.get_purchases_by_user(user_id)

        bot.edit_message_text(
            msg_user_purchases(user_id, purchases),
            chat_id, mes_id,
            reply_markup=kb_user_purchases(user_id)
        )

    if type == 'main':
        send_user_main(bot, call.message, user_id)

    if type == 'back':
        send_user_account(bot, call.message, user_id)

    if type == 'support':
        sup = db.get_support_name()
        msg = msg_support(user_id)

        bot.edit_message_text(
            msg, chat_id, mes_id,
            reply_markup=kb_support(user_id, sup)
        )
        bot.delete_state(user_id, mes_id)

    if type == 'referral':
        send_referral(bot, call.message, user_id)

    if type == 'referral_list':
        user_db_id = db.get_user_id_by_tg_id(user_id)
        referrals = db.get_user_referals(user_db_id)

        text = msg_referral_list(user_id, referrals)

        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_user_referral_list(user_id)
        )

    if type == 'password':
        bot.edit_message_text(
            'Введите новый пароль:', chat_id, mes_id
        )
        bot.set_state(user_id, UserAccountState.password, chat_id)

    if type == 'params':
        send_user_params(bot, call.message, user_id)

    if 'set_lang' in type:
        is_edit_lang = False

        for lang in LANGUAGES:
            if f'_{lang}' in type:
                is_edit_lang = True
                user_db_id = db.get_user_id_by_tg_id(user_id)
                db.set_user_lang(user_db_id, lang)
                send_user_params(bot, call.message, user_id)

        if not is_edit_lang:
            bot.edit_message_text(
                msg_choose_lang(user_id),
                chat_id, mes_id,
                reply_markup=kb_params_choose_lang(user_id)
            )

    if type == 'set_name':
        bot.edit_message_text(
            msg_enter_nickname(user_id), chat_id, mes_id,
            reply_markup=kb_user_params_back(user_id)
        )
        bot.set_state(user_id, UserAccountState.nickname, chat_id)

    if type == 'wallet':
        asyncio.run(walletPage(bot, chat_id, user_id))

    if 'connect++' in type:
        _, wallet = type.split('++')
        asyncio.run(connect_wallet(bot, chat_id, user_id, mes_id, wallet))

    if type == 'wallet_check':
        asyncio.run(check_wallet(bot, chat_id, user_id, mes_id))

    bot.answer_callback_query(call.id)


async def walletPage(bot: TeleBot, chat_id: int, user_id: int):
    connected = await connector.restore_connection()

    if connected:
        # mk_b.button(text='Send Transaction', callback_data='send_tr')
        # mk_b.button(text='Disconnect', callback_data='disconnect')
        # await message.answer(text='You are already connected!', reply_markup=mk_b.as_markup())
        pass
    else:
        wallets_list = TonConnect.get_wallets()  # type: ignore
        wallets_names = [el['name'] for el in wallets_list]
        kb = kb_wallets(user_id, wallets_names)

        bot.send_message(
            chat_id, 'Коннект',
            reply_markup=kb
        )


async def connect_wallet(bot: TeleBot, chat_id: int, user_id: int, mes_id: int, wallet_name: str):
    wallets_list = connector.get_wallets()
    wallet = None

    for w in wallets_list:
        if w['name'] == wallet_name:
            wallet = w

    if wallet is None:
        raise Exception(f'Unknown wallet: {wallet_name}')

    generated_url = await connector.connect(wallet)
    kb = kb_wallet_connect(user_id, generated_url)

    bot.edit_message_text(
        'КОННЕКТ', chat_id, mes_id, reply_markup=kb
    )

    def status_changed(wallet_info):
        # update state/reactive variables to show updates in the ui
        print('wallet_info:', wallet_info)
        unsub()

    unsub = connector.on_status_change(status_changed, status_changed)


async def check_wallet(bot: TeleBot, chat_id: int, user_id: int, mes_id: int):
    if connector.connected and connector.account is not None and connector.account.address:
        wallet_address = connector.account.address
        bot.edit_message_text(
            f'You are connected with address <code>{wallet_address}</code>', chat_id, mes_id,
        )
        return


def registration(bot: TeleBot):
    bot.add_custom_filter(UserAccountCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        user_account=user_account_factory.filter())
