from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from telebot.custom_filters import StateFilter

from config_global import TOKEN_MAIN_BOT

from Middlewares.ChatMemberHandler import chat_member_handler_registration
from Middlewares.AuthMiddleWare import AuthMiddleWare
from Middlewares.ExceptionHandler import ExHandler
from MAIN.commands import commands_registration
from MAIN.handlers import handlers_registration
from MAIN.callbacks import callbacks_registration

from callbacks.calculate import registration as _reg_cb_calculate
from callbacks.main import registration as _reg_cb_main
from callbacks.stats import registration as _reg_cb_stats


bot = TeleBot(
    TOKEN_MAIN_BOT, 'HTML',
    state_storage=StateMemoryStorage(),
    skip_pending=True,
    use_class_middlewares=True,
    exception_handler=ExHandler()
)

bot.setup_middleware(AuthMiddleWare(bot))

commands_registration(bot)

_reg_cb_calculate(bot)
_reg_cb_main(bot)
_reg_cb_stats(bot)

callbacks_registration(bot)
handlers_registration(bot)
chat_member_handler_registration(bot)

bot.add_custom_filter(StateFilter(bot))