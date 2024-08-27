# type: ignore
from telebot import TeleBot as _TB

from .utils import choose_calculate_step, choose_first_calculate_step

from .manual.handler import registration as _reg_manual
from .manual.keyboards import kb_manuals

from .settings.handler import registration as _reg_settings
from .settings.keyboards import (
    kb_settings, kb_base_cancel, kb_settings_confirm,
    kb_change_base, kb_choose_lang, kb_change_currency,
    kb_change_market, kb_splitting_last, kb_take_profit,
    kb_summury_profit, kb_summury_profit_type, kb_splitting,
    kb_trading_style, kb_change_deposit, kb_deposit_cancel,
    kb_trading_type, kb_enter_exchange, kb_choose_exchange_level,
    kb_change_fee, kb_choose_stop_type, kb_change_style_settings,
    kb_round_count
)

from .tariff.handler import registration as _reg_user_tariff
from .tariff.keyboards import (
    kb_tariff_list, kb_choose_products, kb_user_tariff_back, kb_bill
)

from .channel_post.handler import registration as _res_channel_post
from .channel_post.keyboards import (
    kb_channel_post, kb_channel_stat, kb_send_settings,
    kb_send_settings_calc_time, kb_send_settings_trading_style
)

def callbacks_registration(bot: _TB):
    _reg_manual(bot)
    _reg_settings(bot)
    _res_channel_post(bot)

    _reg_user_tariff(bot)