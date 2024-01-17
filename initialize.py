import asyncio

from aiocryptopay import AioCryptoPay, Networks
from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_global import TOKEN_MAIN_BOT
from config_logger import logger

from db import db
from keyboard_inlines import Admin_kb_inlines, Clients_kb_inlines
from GuardPaymentAccess import GuardPaymentAccess
from Payments import Payments
from PaymentsBanker import PaymentsBanker
from TariffManager import TariffManager
from TextEditor import TextEditor


# Криптобот запуск и тест
# cryptopay_token = '122477:AAdtoHbzOKVvVZ2jqSeeSvbS942AcSzWuZO'  # мой токен
cryptopay_token = '127028:AAH1BohV3Nn5oO95yuK5PhRwEZN9VOSW48x'  # продакшен токен
crypto = AioCryptoPay(token=cryptopay_token, network=Networks.MAIN_NET)
bitbanker_token = 'EW3Vz98SfC5xNWe95G8c4R_KEMLXIbwR'
bitbanker_secret = 'xULfhsA-lqGDs7wbq2kOgatekqm2ZW2nYUi33ercK8IQcFIuKvgXmEqj57sPKrdNSYiSgRf26J_D-vBczhuzz-4KYoiFoDw0OBkf2eWHMfp2SfmI4Lxq4uRLwzR5k_bN'


async def start_cryptopay():
    profile = await crypto.get_me()
    # currencies = await crypto.get_currencies()
    balance = await crypto.get_balance()
    rates = await crypto.get_exchange_rates()
    # print(profile, currencies, balance, rates, sep='\n')
    logger.info(f'-----> Криптобот удачно запустился profile:')
    logger.info(profile)
    logger.info(f'-----> Криптобот баланс:')
    logger.info(balance)

    async def close_session() -> None:
        await crypto.close()

asyncio.run(start_cryptopay())

state_storage = StateMemoryStorage()
bot = TeleBot(
    TOKEN_MAIN_BOT, 'HTML',
    state_storage=state_storage,
    skip_pending=True,
    use_class_middlewares=True
)

pay_guard = GuardPaymentAccess(db)
pays = Payments(db, token=cryptopay_token, network=Networks.MAIN_NET)
pays_banker = PaymentsBanker(
    api_key=bitbanker_token, api_secret=bitbanker_secret, bot_instance=bot)
pays_banker.set_field_invoice('firm_name_header', 'THE CLAN')


kb_inl_admin = Admin_kb_inlines()
kb_inl_user = Clients_kb_inlines()

text_editor = TextEditor(db, bot, kb_inl_admin)
tariff_manager = TariffManager(db, bot, kb_inl_admin, kb_inl_user)
