from telebot import TeleBot as _TB

from .admin.pages import send_admin_post
from .user.pages import send_user_education, send_user_main, send_user_terms, send_user_account
from .calculator.pages import send_main, send_settings, send_manual_page
from .calculator.utils import choose_calculate_step, choose_first_calculate_step

from .admin.workers.handler import registration as _reg_admin_workers
from .admin.workers.keyboards import kb_admin_workers_update, kb_admin_workers_actions

from .admin.users.handler import registration as _reg_admin_users
from .admin.users.keyboards import kb_admin_users, kb_admin_users_back

from .admin.params.handler import registration as _reg_admin_params
from .admin.params.keyboards import (kb_params_change, kb_calculator, kb_params,
                                     kb_params_back, kb_params_choice)

from .admin.posts.handler import registration as _reg_admin_posts
from .admin.posts.keyboards import kb_posts, kb_posts_back, kb_post_add_confirm, kb_post_confirm, kb_post_kinds


from .user.main.handler import registration as _reg_user_main
from .user.main.keyboards import kb_user_main, kb_user_calculator

from .user.education.handler import registration as _reg_user_education
from .user.education.keyboards import kb_user_education, kb_user_curs, kb_user_pages

from .user.account.handler import registration as _reg_user_account
from .user.account.keyboards import kb_user_account, kb_user_referral, kb_user_referral_list


from .calculator.manual.handler import registration as _reg_manual
from .calculator.manual.keyboards import kb_manual

from .calculator.main.handler import registration as _reg_main
from .calculator.main.keyboards import kb_main, kb_cancel, cancel_btn, kb_forex_val

from .calculator.settings.handler import registration as _reg_settings
from .calculator.settings.keyboards import kb_settings, kb_base_cancel, kb_settings_confirm, kb_change_base, kb_choose_lang


def callbacks_registration(bot: _TB):
    _reg_admin_workers(bot)
    _reg_admin_params(bot)
    _reg_admin_posts(bot)
    _reg_admin_users(bot)

    _reg_user_main(bot)
    _reg_user_education(bot)
    _reg_user_account(bot)
    _reg_manual(bot)
    _reg_main(bot)
    _reg_settings(bot)