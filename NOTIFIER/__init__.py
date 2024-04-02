from .initialize import bot_new_user_notifier as _bot_users
from .initialize import bot_notifier as _bot
from .Notifier import Notifier as _Notifier

notifier = _Notifier(_bot, _bot_users)