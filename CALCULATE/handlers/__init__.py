from telebot import TeleBot as _TB

from .calculate import registration as _reg_calculate
from .settings import registration as _reg_settings
from .stats import registration as _reg_stats


def handlers_registration(bot: _TB):
    _reg_calculate(bot)
    _reg_settings(bot)
    _reg_stats(bot)
