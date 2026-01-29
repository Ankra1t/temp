from telebot.async_telebot import AsyncTeleBot
from telebot.states.asyncio.middleware import StateMiddleware

from Middlewares.ChatMemberHandler import chat_member_handler_registration
from Middlewares.AuthMiddleWare import AuthMiddleWare
from commands import commands_registration
from models import StateFilter

from callbacks.calculate import registration as _reg_cb_calculate
from callbacks.main import registration as _reg_cb_main
from callbacks.stats import registration as _reg_cb_stats
from callbacks.channel_post import registration as _reg_cb_channel_post
from callbacks.manual import registration as _reg_cb_manual
from callbacks.settings import registration as _reg_cb_settings
from callbacks.education import registration as _reg_cb_education
from callbacks.account import registration as _reg_cb_account

from callbacks.admin_main import registration as _reg_cb_admin_main
from callbacks.admin_params import registration as _reg_cb_admin_params
from callbacks.admin_stats import registration as _reg_cb_admin_stats
from callbacks.admin_subs import registration as _reg_cb_admin_subs
from callbacks.admin_users import registration as _reg_cb_admin_users
from callbacks.user_main import registration as _reg_cb_user_main

from callbacks.livepost import registration as _reg_cb_livepost

from handlers.admin_stats import registration as _reg_admin_statistics
from handlers.admin_users import registration as _reg_admin_users
from handlers.admin_params import registration as _reg_admin_params

from handlers.account import registration as _reg_user_account

from handlers.calculate import registration as _reg_calc
from handlers.settings import registration as _reg_settings
from handlers.stats import registration as _reg_stats


def reg(bot: AsyncTeleBot):
    bot.setup_middleware(AuthMiddleWare(bot))
    bot.setup_middleware(StateMiddleware(bot))

    commands_registration(bot)

    _reg_cb_manual(bot)
    _reg_cb_main(bot)
    _reg_cb_calculate(bot)
    _reg_cb_settings(bot)
    _reg_cb_stats(bot)
    _reg_cb_channel_post(bot)

    _reg_cb_admin_main(bot)
    _reg_cb_admin_params(bot)
    _reg_cb_admin_users(bot)
    _reg_cb_admin_stats(bot)

    _reg_cb_user_main(bot)
    _reg_cb_education(bot)
    _reg_cb_account(bot)

    _reg_cb_livepost(bot)

    _reg_admin_statistics(bot)
    _reg_admin_users(bot)
    _reg_admin_params(bot)
    _reg_cb_admin_subs(bot)

    _reg_user_account(bot)

    _reg_calc(bot)
    _reg_settings(bot)
    _reg_stats(bot)

    chat_member_handler_registration(bot)

    bot.add_custom_filter(StateFilter(bot))
