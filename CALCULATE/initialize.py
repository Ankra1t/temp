from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from telebot.custom_filters import StateFilter

from AuthMiddleWare import AuthMiddleWare
from config_global import TOKEN_CALC_BOT

from CALCULATE.commands import commands_registration
from CALCULATE.handlers import handlers_registration
from CALCULATE.callbacks import callbacks_registration


bot_calc = TeleBot(
    TOKEN_CALC_BOT, 'HTML',
    state_storage=StateMemoryStorage(),
    skip_pending=True,
    use_class_middlewares=True
)

bot_calc.setup_middleware(AuthMiddleWare(bot_calc))


commands_registration(bot_calc)
callbacks_registration(bot_calc)
handlers_registration(bot_calc)


bot_calc.add_custom_filter(StateFilter(bot_calc))
