from telebot import TeleBot as _TB

from .admin.pages import send_admin_post, send_admin_client, send_admin_workers, send_admin_workers_support
from .user.pages import send_user_education, send_user_main, send_user_terms, send_user_account

from .admin.workers.handler import registration as _reg_admin_workers
from .admin.workers.keyboards import (
    kb_admin_workers_confirm, kb_admin_workers_actions, kb_admin_workers_back,
    kb_admin_workers, kb_admin_workers_support
)

from .admin.users.handler import registration as _reg_admin_users
from .admin.users.keyboards import (
    kb_admin_users, kb_admin_users_back, kb_admin_users_list,
    kb_admin_client_info, kb_admin_users_confirm, kb_admin_users_cancel
)

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

from CALCULATE.callbacks import callbacks_registration as _reg_calculator


def callbacks_registration(bot: _TB):
    _reg_admin_workers(bot)
    _reg_admin_params(bot)
    _reg_admin_posts(bot)
    _reg_admin_users(bot)

    _reg_user_main(bot)
    _reg_user_education(bot)
    _reg_user_account(bot)

    _reg_calculator(bot)
