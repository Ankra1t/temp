from aiocryptopay import Networks

from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_global import TOKEN_MAIN_BOT, cryptopay_token, bitbanker_token, bitbanker_secret
from config_logger import logger

from db import db
from keyboard_inlines import Admin_kb_inlines, Clients_kb_inlines
from GuardPaymentAccess import GuardPaymentAccess
from Payments import Payments
from PaymentsBanker import PaymentsBanker
from TariffManager import TariffManager
from TextEditor import TextEditor


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
