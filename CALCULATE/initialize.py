from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from telebot.custom_filters import StateFilter

from AuthMiddleWare import AuthMiddleWare
from config_global import TOKEN_CALC_BOT, _ENV

from CALCULATE.commands import commands_registration
from CALCULATE.handlers import handlers_registration
from CALCULATE.callbacks import callbacks_registration
from CALCULATE.callback import callback_inline


bot_calc = TeleBot(
    TOKEN_CALC_BOT, 'HTML',
    state_storage=StateMemoryStorage(),
    skip_pending=True,
    use_class_middlewares=True
)

bot_calc.setup_middleware(AuthMiddleWare(bot_calc))


def registration():
    bot_calc.register_callback_query_handler(
        callback_inline, func=lambda call: True, pass_bot=True)


commands_registration(bot_calc)
callbacks_registration(bot_calc)
handlers_registration(bot_calc)
registration()


bot_calc.add_custom_filter(StateFilter(bot_calc))


if _ENV == 'calc':
    bot_calc.infinity_polling()
