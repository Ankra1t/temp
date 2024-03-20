from aiocryptopay import Networks

from aiocryptopay import AioCryptoPay, Networks
from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_global import CURRENCYAPI_KEY, TOKEN_MAIN_BOT, cryptopay_token, bitbanker_token, bitbanker_secret
from config_logger import logger

from db_new import db_new
from keyboard_inlines import Admin_kb_inlines, Clients_kb_inlines
from GuardPaymentAccess import GuardPaymentAccess
from Payments import Payments
from PaymentsBanker import PaymentsBanker
from TariffManager import TariffManager
from TextEditor import TextEditor
from Classes.BaseStatistics import BaseStatistics
from Classes.ServiceTasks import ServiceTasks
from Classes.CalculationService import CalculationService
from Classes.CurrencyService import CurrencyService


state_storage = StateMemoryStorage()
bot = TeleBot(
    TOKEN_MAIN_BOT, 'HTML',
    state_storage=state_storage,
    skip_pending=True,
    use_class_middlewares=True
)


pay_guard = GuardPaymentAccess()
pays = Payments(token=cryptopay_token, network=Networks.MAIN_NET)
base_statis = BaseStatistics(db_new, bot)
serv_tasks = ServiceTasks(db_new, bot)

pays_banker = PaymentsBanker(
    api_key=bitbanker_token, api_secret=bitbanker_secret, bot_instance=bot)
pays_banker.set_field_invoice('firm_name_header', 'THE CLAN')

calcService = CalculationService(bot, db_new)
currencyService = CurrencyService(CURRENCYAPI_KEY)


kb_inl_admin = Admin_kb_inlines()
kb_inl_user = Clients_kb_inlines()

text_editor = TextEditor(bot, kb_inl_admin)
tariff_manager = TariffManager(bot, kb_inl_admin, kb_inl_user)
