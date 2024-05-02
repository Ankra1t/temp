from telebot import TeleBot
from telebot.types import ChatMemberUpdated

from db import db


def _handler(member: ChatMemberUpdated):
    user_db_id = db.get_user_id_by_tg_id(member.from_user.id)
    if member.new_chat_member.status == 'kicked':
        db.set_user_tg_block(user_db_id, True)
    else:
        db.set_user_tg_block(user_db_id, False)


def chat_member_handler_registration(bot: TeleBot):
    bot.register_my_chat_member_handler(_handler)
