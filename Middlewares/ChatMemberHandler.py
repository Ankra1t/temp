from telebot.async_telebot import AsyncTeleBot
from telebot.types import ChatMemberUpdated

from NOTIFIER import notifier
from db import db
from services import auth


async def _handler(member: ChatMemberUpdated):
    user_db_id = db.get_user_id_by_tg_id(member.from_user.id)
    if member.new_chat_member.status == 'kicked':
        db.set_user_tg_block(user_db_id, True)

        sent_messages = auth.getUserNotificationMessages(user_db_id)

        if sent_messages:
            await notifier.change_user_blocked(user_db_id, sent_messages)
    else:
        db.set_user_tg_block(user_db_id, False)


def chat_member_handler_registration(bot: AsyncTeleBot):
    bot.register_my_chat_member_handler(_handler)
