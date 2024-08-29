from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from telebot.custom_filters import StateFilter

from config_global import TOKEN_MAIN_BOT

from Middlewares.ChatMemberHandler import chat_member_handler_registration
from Middlewares.AuthMiddleWare import AuthMiddleWare
from Middlewares.ExceptionHandler import ExHandler
from commands import commands_registration

from callbacks.calculate import registration as _reg_cb_calculate
from callbacks.main import registration as _reg_cb_main
from callbacks.stats import registration as _reg_cb_stats
from callbacks.channel_post import registration as _reg_cb_channel_post
from callbacks.manual import registration as _reg_cb_manual
from callbacks.settings import registration as _reg_cb_settings
from callbacks.tariff import registration as _reg_cb_tariff
from callbacks.education import registration as _reg_cb_education
from callbacks.account import registration as _reg_cb_account

from callbacks.admin_main import registration as _reg_cb_admin_main
from callbacks.admin_params import registration as _reg_cb_admin_params
from callbacks.admin_posts import registration as _reg_cb_admin_posts
from callbacks.admin_stats import registration as _reg_cb_admin_stats
from callbacks.admin_tariffs import registration as _reg_cb_admin_tariffs
from callbacks.admin_workers import registration as _reg_cb_admin_workers
from callbacks.admin_users import registration as _reg_cb_admin_users
from callbacks.user_main import registration as _reg_cb_user_main

from callbacks.livepost import registration as _reg_cb_livepost

from handlers.admin_tariff import registration as _reg_admin_tariff
from handlers.admin_stats import registration as _reg_admin_statistics
from handlers.admin_workers import registration as _reg_admin_workers
from handlers.admin_users import registration as _reg_admin_users
from handlers.admin_params import registration as _reg_admin_params
from handlers.admin_posts import registration as _reg_admin_posts

from handlers.account import registration as _reg_user_account

from handlers.livepost import registration as _reg_livepost

from handlers.calculate import registration as _reg_calc
from handlers.settings import registration as _reg_settings
from handlers.stats import registration as _reg_stats
from handlers.tariff import registration as _reg_tariff


bot = TeleBot(
    TOKEN_MAIN_BOT, 'HTML',
    state_storage=StateMemoryStorage(),
    skip_pending=True,
    use_class_middlewares=True,
    exception_handler=ExHandler()
)

bot.setup_middleware(AuthMiddleWare(bot))

commands_registration(bot)

_reg_cb_manual(bot)
_reg_cb_main(bot)
_reg_cb_calculate(bot)
_reg_cb_settings(bot)
_reg_cb_stats(bot)
_reg_cb_channel_post(bot)
_reg_cb_tariff(bot)

_reg_cb_admin_main(bot)
_reg_cb_admin_tariffs(bot)
_reg_cb_admin_workers(bot)
_reg_cb_admin_params(bot)
_reg_cb_admin_posts(bot)
_reg_cb_admin_users(bot)
_reg_cb_admin_stats(bot)

_reg_cb_user_main(bot)
_reg_cb_education(bot)
_reg_cb_account(bot)

_reg_cb_livepost(bot)

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

chat_member_handler_registration(bot)

bot.add_custom_filter(StateFilter(bot))
