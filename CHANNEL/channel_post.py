from telebot.async_telebot import AsyncTeleBot

from Middlewares.ExceptionHandler import ExHandler
from config_global import TOKEN_CHANNEL_BOT

from .ChannelPost import ChannelPost

from initialize import bot as main_bot

channel_bot = AsyncTeleBot(
    TOKEN_CHANNEL_BOT, 'HTML',
    exception_handler=ExHandler(),
)

channel_post = ChannelPost(channel_bot, main_bot)
