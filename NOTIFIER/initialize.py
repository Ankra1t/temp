from telebot.async_telebot import AsyncTeleBot

from config_global import TOKEN_NOT_USER_BOT
from config_global import TOKEN_NOT_BOT


bot_new_user_notifier = AsyncTeleBot(TOKEN_NOT_USER_BOT, 'HTML')
bot_notifier = AsyncTeleBot(TOKEN_NOT_BOT, 'HTML')
