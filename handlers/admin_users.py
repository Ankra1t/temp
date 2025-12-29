from telebot.async_telebot import AsyncTeleBot

from models import Message, StateContext, User

from common.utils import is_digit, text_accept


from states.admin_users import AdminUsersState
from keyboards.admin_users import kb_admin_users_cancel


async def handle_client_search(message: Message, bot: AsyncTeleBot, state: StateContext):
    user_id = message.from_user.id
    chat_id = message.chat.id

    async with state.data() as data:
        sort_by = data.get('sort_by') or ''
        page = data.get('page') or 1

    client_name_id = text_accept(message)
    if client_name_id is None:
        await bot.send_message(
            chat_id,
            'Введите id или имя пользователя текстом:',
            reply_markup=kb_admin_users_cancel(sort_by, page)
        )
        return

    if is_digit(client_name_id):
        client_db_id = int(float(client_name_id))
    else:
        client_name_id = client_name_id.replace('@', '')
        # client_db_id = db.get_user_id_by_tg_name(client_name_id)

    # client = db.get_user_by_id(client_db_id)

    # if client is None:
    #     await bot.send_message(
    #         chat_id,
    #         'Пользователя не существует.\nВведите id или имя пользователя:',
    #         reply_markup=kb_admin_users_cancel(sort_by, page)
    #     )
    #     return

    # await send_admin_client(
    #     bot, message, state,
    #     client.id,
    #     sort_by, page, True
    # )

    await bot.send_message(chat_id, 'В разработке')

    await state.delete()


async def handle_days_subscribe(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    # Убрано (подписки/оплата)
    await bot.send_message(chat_id, 'Функция подписок отключена')
    await state.delete()


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_client_search, state=AdminUsersState.client_search)

    reg_mes(handle_days_subscribe, state=AdminUsersState.subscribe_days)

    reg_mes(handle_days_subscribe,
            state=AdminUsersState.trial_subscribe_days_get_days)
