from aiocryptopay import Networks

from aiocryptopay import Networks
from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_global import CURRENCYAPI_KEY, TOKEN_MAIN_BOT, cryptopay_token, bitbanker_token, bitbanker_secret

from db import db
from Classes.GuardPaymentAccess import GuardPaymentAccess
from Classes.Payments import Payments
from Classes.TariffManager import TariffManager
from Classes.TextEditor import TextEditor

from Classes.PaymentsBanker import PaymentsBanker
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
base_statis = BaseStatistics(db, bot)
serv_tasks = ServiceTasks(db, bot)

pays_banker = PaymentsBanker(
    api_key=bitbanker_token, api_secret=bitbanker_secret, bot_instance=bot)
pays_banker.set_field_invoice('firm_name_header', 'THE CLAN')

calcService = CalculationService(bot, db)
currencyService = CurrencyService(CURRENCYAPI_KEY)


text_editor = TextEditor(bot)
tariff_manager = TariffManager(bot)
