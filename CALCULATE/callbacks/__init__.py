from telebot import TeleBot as _TB

from .pages import send_main, send_settings, send_manual_page, send_summury_profit_settings, send_stats
from .utils import choose_calculate_step, choose_first_calculate_step

from .manual.handler import registration as _reg_manual
from .manual.keyboards import kb_manual

from .main.handler import registration as _reg_main
from .main.keyboards import kb_main, kb_main_cancel, cancel_btn, kb_forex_val

from .stats.handler import registration as _reg_stats
from .stats.keyboards import kb_stats, kb_set_calc_stats, kb_freeze_calc, kb_deal_result, kb_deal_profit_minus

from .settings.handler import registration as _reg_settings
from .settings.keyboards import (
    kb_settings, kb_base_cancel, kb_settings_confirm,
    kb_change_base, kb_choose_lang, kb_change_currency,
    kb_change_market, kb_splitting_last, kb_take_profit,
    kb_summury_profit, kb_summury_profit_type, kb_splitting,
    kb_trading_style
)


def callbacks_registration(bot: _TB):
    _reg_manual(bot)
    _reg_main(bot)
    _reg_settings(bot)
    _reg_stats(bot)
