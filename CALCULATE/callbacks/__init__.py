# type: ignore
from telebot import TeleBot as _TB

from .pages import (
    send_main, send_settings, send_manual_page,
    send_summury_profit_settings, send_stats, send_user_deposit,
    send_tariffs_list_item, send_user_tariffs, send_calculation
)
from .utils import choose_calculate_step, choose_first_calculate_step

from .manual.handler import registration as _reg_manual
from .manual.keyboards import kb_manual

from .main.handler import registration as _reg_main
from .main.keyboards import kb_main, cancel_btn

from .calculate.handler import registration as _reg_calculate
from .calculate.keyboards import kb_pair, kb_tool, kb_price, kb_calc_cancel

from .stats.handler import registration as _reg_stats
from .stats.keyboards import (
    kb_stats, kb_calc_result, kb_freeze_calc,
    kb_deal_result, kb_deal_profit_minus, kb_deal_profit_cancel,
    kb_calculate_delete, kb_calculate_change, kb_calc_image
)

from .settings.handler import registration as _reg_settings
from .settings.keyboards import (
    kb_settings, kb_base_cancel, kb_settings_confirm,
    kb_change_base, kb_choose_lang, kb_change_currency,
    kb_change_market, kb_splitting_last, kb_take_profit,
    kb_summury_profit, kb_summury_profit_type, kb_splitting,
    kb_trading_style, kb_change_deposit, kb_deposit_cancel,
    kb_trading_type
)

from .tariff.handler import registration as _reg_user_tariff
from .tariff.keyboards import (
    kb_tariff_list, kb_choose_products, kb_user_tariff_back, kb_bill
)


def callbacks_registration(bot: _TB):
    _reg_manual(bot)
    _reg_main(bot)
    _reg_calculate(bot)
    _reg_settings(bot)
    _reg_stats(bot)

    _reg_user_tariff(bot)