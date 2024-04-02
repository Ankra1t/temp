from telebot import TeleBot

from config_global import TOKEN_NOT_USER_BOT
from config_global import TOKEN_NOT_BOT


bot_new_user_notifier = TeleBot(TOKEN_NOT_USER_BOT, 'HTML')
bot_notifier = TeleBot(TOKEN_NOT_BOT, 'HTML')
