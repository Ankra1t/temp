import os
from telebot.async_telebot import AsyncTeleBot

from config_logger import logger
from AuthRoles import check_registration
from common.utils import delete_message
from common.utils import get_post_from_message
from states.admin_posts import AdminPostsState

from keyboards.admin_posts import kb_posts_back
from keyboards.livepost import kb_livepost_type
from pages.calculate import send_admin_channel_calc_item, send_calculation

from services import calculation, twitter
from models import Message, StateContext, User
from db import db

async def handle_livepost(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    print(message.html_text)
    mes_id = message.id
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.content_type == 'text' and message.text is not None:
        text = message.text

        type = str(await state.get())

        if text.startswith('/') and type == 'handle_calc_id':
            await delete_message(bot, chat_id, mes_id)

            text = text.replace('/', '')
            if not text.isdigit():
                return

            calc_id = int(text)
            await send_admin_channel_calc_item(
                bot, message, state, calc_id, is_first=True
            )

            return

        if text.startswith('/') and 'user_calc_id' in type:
            await delete_message(bot, chat_id, mes_id)

            text = text.replace('/', '')

            if '_' in text:
                tool, count = text.split('_')
            else:
                tool, count = text, 1

            res_id = 0

            user_db_id = db.get_user_id_by_tg_id(user_id)
            if 'live' in type:
                data = calculation.getWeekStats(userId=user_db_id)
                if not data:
                    return
                num = 0

                for item in data:
                    calcs = item.get('calcs', [])
                    for calc in calcs:
                        if tool == calc.get('tool').replace('/USDT', ''):
                            num += 1
                        if num == int(count):
                            res_id = calc.get('id')
                            break
                    if res_id != 0:
                        break
            else:
                list_type = type.split(' ')[1]
                data = calculation.getByUserList(
                    user_db_id, list_type)  # type: ignore
                if data is None:
                    return

                num = 0

                for el in data:
                    if (el.tool or "").replace('/USDT', '') == tool:
                        num += 1
                        if num == int(count):
                            res_id = el.id
                            break

            calc_id = int(res_id)
            calc = calculation.get(userId=user.id, calcId=calc_id)
            if calc is None:
                return

            await send_calculation(bot, message, state, user, calc, is_first=True, is_list=True)
            return

    if message.photo:
        file_id = message.photo[-1].file_id
        logger.info(file_id)
        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)

        name = f'{file_id}.png'
        with open(name, 'wb') as new_file:
            new_file.write(file_bytes)

        with open(name, 'rb') as file:
            data = twitter.create(file)
            logger.info(data)

        os.remove(name)


    # livepost
    user_role = check_registration(user_id)
    if user_role != 1 and user_role != 2:
        return

    try:
        print(message.html_text)
        if message.animation:
            print(message.animation.file_id)
        if message.photo:
            print(message.photo[-1].file_id)
    except:
        pass

    post = await get_post_from_message(bot, message, kb_posts_back)

    if post is None:
        return

    await state.set(AdminPostsState.live)
    await state.add_data(post=post, kind='live')

    await bot.send_message(
        chat_id, 'Выберите действие:',
        reply_markup=kb_livepost_type()
    )


def registration(bot: AsyncTeleBot):
    bot.register_message_handler(
        handle_livepost, # type: ignore
        content_types=['photo', 'video', 'text', 'animation'],
        pass_bot=True
    )
