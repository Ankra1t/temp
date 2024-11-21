from .initialize import bot_new_user_notifier as _bot_users, bot_notifier as _bot, bot_site_user_notifier as _bot_site_user_notifier
from .Notifier import Notifier as _Notifier

notifier = _Notifier(_bot, _bot_users, _bot_site_user_notifier)
