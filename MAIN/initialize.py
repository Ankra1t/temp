from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from telebot.custom_filters import StateFilter

from AuthMiddleWare import AuthMiddleWare
from config_global import TOKEN_MAIN_BOT

from MAIN.commands import commands_registration
from MAIN.handlers import handlers_registration
from MAIN.callbacks import callbacks_registration


bot = TeleBot(
    TOKEN_MAIN_BOT, 'HTML',
    state_storage=StateMemoryStorage(),
    skip_pending=True,
    use_class_middlewares=True,
)

bot.setup_middleware(AuthMiddleWare(bot))

commands_registration(bot)
callbacks_registration(bot)
handlers_registration(bot)

bot.add_custom_filter(StateFilter(bot))