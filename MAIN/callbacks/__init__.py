# type: ignore
from telebot import TeleBot as _TB

from .admin.pages import (
    send_admin_post, send_admin_client,
    send_admin_workers, send_admin_workers_support,
    send_admin_workers_admin, send_admin_workers_support,
    send_admin_main, send_admin_users, send_admin_payment,
    send_admin_fut_posts, send_admin_params, send_admin_tariffs_list_item
)
from .user.pages import (
    send_user_education, send_user_main, send_user_terms,
    send_user_account, send_site_code, send_user_tariffs,
    send_tariffs_list_item
)

from .common.livepost.handler import registration as _reg_livepost
from .common.livepost.keyboards import kb_livepost_cancel, kb_livepost_type


from .admin.main.handler import registration as _reg_admin_main
from .admin.main.keyboards import (
    kb_admin_main
)

from .admin.tariffs.handler import registration as _reg_admin_tariffs
from .admin.tariffs.keyboards import (
    kb_admin_tariffs, kb_admin_tariffs_list, kb_admin_tariffs_back,
    kb_admin_tariffs_delete, kb_admin_tariffs_list_back, kb_admin_tariffs_edit,
    kb_admin_tariff_add_type
)

from .admin.workers.handler import registration as _reg_admin_workers
from .admin.workers.keyboards import (
    kb_admin_workers_confirm, kb_admin_workers_actions, kb_admin_workers_back,
    kb_admin_workers, kb_admin_workers_support
)

from .admin.users.handler import registration as _reg_admin_users
from .admin.users.keyboards import (
    kb_admin_users, kb_admin_users_back, kb_admin_client_list,
    kb_admin_client_info, kb_admin_users_confirm, kb_admin_users_cancel, kb_admin_choose_periods,
    kb_admin_choose_list
)

from .admin.params.handler import registration as _reg_admin_params
from .admin.params.keyboards import (
    kb_params_change, kb_calculator, kb_params,
    kb_params_back, kb_params_choice, kb_edit_text
)

from .admin.statistics.handler import registration as _reg_admin_statistics
from .admin.statistics.keyboards import kb_statistics, kb_statistics_back

from .admin.posts.handler import registration as _reg_admin_posts
from .admin.posts.keyboards import kb_posts, kb_posts_back, kb_post_add_confirm, kb_post_confirm, kb_post_kinds


from .user.main.handler import registration as _reg_user_main
from .user.main.keyboards import kb_user_main, kb_user_calculator, kb_site_login

from .user.education.handler import registration as _reg_user_education
from .user.education.keyboards import kb_user_education, kb_user_curs, kb_user_pages

from .user.account.handler import registration as _reg_user_account
from .user.account.keyboards import kb_user_account, kb_user_referral, kb_user_referral_list

from .user.tariff.handler import registration as _reg_user_tariff
from .user.tariff.keyboards import (
    kb_tariff_list, kb_bill_bitbanker, kb_bill_cryptobot,
    kb_bill_many, kb_choose_products, kb_user_tariff_back
)

from CALCULATE.callbacks import callbacks_registration as _reg_calculator


def callbacks_registration(bot: _TB):
    _reg_admin_main(bot)
    _reg_admin_tariffs(bot)
    _reg_admin_workers(bot)
    _reg_admin_params(bot)
    _reg_admin_posts(bot)
    _reg_admin_users(bot)
    _reg_admin_statistics(bot)

    _reg_user_main(bot)
    _reg_user_education(bot)
    _reg_user_account(bot)
    _reg_user_tariff(bot)

    _reg_calculator(bot)

    _reg_livepost(bot)
