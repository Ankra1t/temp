from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage

from config_global import TOKEN_MAIN_BOT

from Middlewares.ExceptionHandler import ExHandler

bot = AsyncTeleBot(
    TOKEN_MAIN_BOT, 'HTML',
    state_storage=StateMemoryStorage(),
    exception_handler=ExHandler(),
)
