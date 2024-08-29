from telebot import TeleBot as _TB

from .admin.tariff import registration as _reg_admin_tariff
from .admin.statistics import registration as _reg_admin_statistics
from .admin.workers import registration as _reg_admin_workers
from .admin.users import registration as _reg_admin_users
from .admin.params import registration as _reg_admin_params
from .admin.posts import registration as _reg_admin_posts

from .user.account import registration as _reg_user_account

from .common.livepost import registration as _reg_livepost

from handlers.calculate import registration as _reg_calc
from handlers.settings import registration as _reg_settings
from handlers.stats import registration as _reg_stats
from handlers.tariff import registration as _reg_tariff


def handlers_registration(bot: _TB):
    _reg_admin_tariff(bot)
    _reg_admin_statistics(bot)
    _reg_admin_workers(bot)
    _reg_admin_users(bot)
    _reg_admin_params(bot)
    _reg_admin_posts(bot)

    _reg_user_account(bot)

    _reg_calc(bot)
    _reg_settings(bot)
    _reg_stats(bot)
    _reg_tariff(bot)

    _reg_livepost(bot)  # !Должен регестрироваться последним
