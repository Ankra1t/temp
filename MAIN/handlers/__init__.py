from telebot import TeleBot as _TB

from .admin.tariff import registration as _reg_admin_tariff
from .admin.workers import registration as _reg_admin_workers
from .admin.users import registration as _reg_admin_users
from .admin.params import registration as _reg_admin_params
from .admin.posts import registration as _reg_admin_posts

from .user.account import registration as _reg_user_account

from CALCULATE.handlers import handlers_registration as _reg_calculator


def handlers_registration(bot: _TB):
    _reg_admin_tariff(bot)
    _reg_admin_workers(bot)
    _reg_admin_users(bot)
    _reg_admin_params(bot)
    _reg_admin_posts(bot)

    _reg_user_account(bot)

    _reg_calculator(bot)
