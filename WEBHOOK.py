import asyncio
import logging
from config_logger import logger
from telebot.types import BotCommand

from config_global import PROD

from initialize import bot
from registration import reg


async def setup():
    if PROD:
        logging.basicConfig(level=logging.INFO)

    await bot.remove_webhook()

    commands = [
        ('start', 'restart'),
        ('menu', 'menu'),
        ('calculator', 'calc'),
        ('settings', 'settings'),
        ('referral', 'partner'),
    ]

    await bot.set_my_commands([
        BotCommand(
            command=el[0],
            description=el[1],
        ) for el in commands
    ])

    reg(bot)

    logger.info('Starting up')
    await bot.infinity_polling()


if __name__ == '__main__':
    asyncio.run(setup())
