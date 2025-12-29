from telebot.async_telebot import AsyncTeleBot
from telebot.types import ChatMemberUpdated


async def _handler(member: ChatMemberUpdated):
    pass


def chat_member_handler_registration(bot: AsyncTeleBot):
    bot.register_my_chat_member_handler(_handler)
