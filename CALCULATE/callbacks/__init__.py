from telebot import TeleBot as _TB

from .pages import send_main, send_settings, send_manual_page, send_summury_profit_settings
from .utils import choose_calculate_step, choose_first_calculate_step

from .manual.handler import registration as _reg_manual
from .manual.keyboards import kb_manual

from .main.handler import registration as _reg_main
from .main.keyboards import kb_main, kb_cancel, cancel_btn, kb_forex_val

from .settings.handler import registration as _reg_settings
from .settings.keyboards import (
    kb_settings, kb_base_cancel, kb_settings_confirm,
    kb_change_base, kb_choose_lang, kb_change_currency,
    kb_change_market, kb_change_tp_ratio, kb_split_settings,
    kb_split_ok, kb_summury_profit, kb_summury_profit_type,
    kb_summury_profit_cancel, kb_take_profit, kb_splitting
)


def callbacks_registration(bot: _TB):
    _reg_manual(bot)
    _reg_main(bot)
    _reg_settings(bot)
