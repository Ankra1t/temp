from aiocryptopay import Networks

from aiocryptopay import AioCryptoPay, Networks
from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_global import TOKEN_MAIN_BOT, cryptopay_token, bitbanker_token, bitbanker_secret
from config_logger import logger

from common.vars import DATE_FORMAT, PRINT_DATE_FROMAT


from db_new import db_new
from keyboard_inlines import Admin_kb_inlines, Clients_kb_inlines
from GuardPaymentAccess import GuardPaymentAccess
from Payments import Payments
from PaymentsBanker import PaymentsBanker
from TariffManager import TariffManager
from TextEditor import TextEditor
from Classes.BaseStatistics import BaseStatistics


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

base_statis.dt_format = DATE_FORMAT
base_statis.dt_format_admin_show = PRINT_DATE_FROMAT

pays_banker = PaymentsBanker(
    api_key=bitbanker_token, api_secret=bitbanker_secret, bot_instance=bot)
pays_banker.set_field_invoice('firm_name_header', 'THE CLAN')


kb_inl_admin = Admin_kb_inlines()
kb_inl_user = Clients_kb_inlines()

text_editor = TextEditor(bot, kb_inl_admin)
tariff_manager = TariffManager(bot, kb_inl_admin, kb_inl_user)
