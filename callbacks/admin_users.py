from telebot.async_telebot import AsyncTeleBot
from telebot.types import InaccessibleMessage

from models import SORT_BY_TYPE, CallbackQuery, StateContext, User

from states.admin_users import AdminUsersState

from pages.admin import send_admin_main, send_admin_users

from keyboards.admin_users import (
    admin_users_factory, AdminUsersCallbackFilter,
    kb_admin_choose_list, kb_admin_users_cancel
)


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot, state: StateContext, user: User):
    if isinstance(call.message, InaccessibleMessage) or call.data is None:
        return

    callback_data = admin_users_factory.parse(call.data)

    type: str = callback_data.get('type', '')
    sort_by: SORT_BY_TYPE = callback_data.get(
        'sort_by', 'new'
    )  # type: ignore
    filter: str = callback_data.get('filter', '')
    page = int(callback_data.get('page', 1))

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'go_main':
        await send_admin_main(bot, call.message, state)

    if type == 'go_users':
        await send_admin_users(bot, call.message, state)

    if type == 'lists':
        await bot.edit_message_text(
            'Выберите <u>список</u> клиентов', chat_id, mes_id,
            reply_markup=kb_admin_choose_list()
        )

    if type == 'client_list':
        # TODO: Получить пользователей из API
        await bot.edit_message_text(
            'Список клиентов временно недоступен', chat_id, mes_id,
            reply_markup=kb_admin_users_cancel(sort_by, page, filter)
        )

    if type == 'client_ban':
        # TODO: Получить пользователя из API
        await bot.edit_message_text(
            'Функция временно недоступна', chat_id, mes_id,
            reply_markup=kb_admin_users_cancel(sort_by, page, filter)
        )

    if type == 'client_search':
        await bot.edit_message_text(
            'Введите id или имя пользователя:',
            chat_id, mes_id,
            reply_markup=kb_admin_users_cancel(sort_by, page)
        )
        await state.set(AdminUsersState.client_search)
        await state.add_data(
            sort_by=sort_by,
            page=page
        )

    if type == 'markets':
        # TODO: Получить статистику по рынкам из API
        await bot.edit_message_text(
            'Статистика по рынкам временно недоступна', chat_id, mes_id,
            reply_markup=kb_admin_users_cancel(sort_by, page, filter)
        )

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminUsersCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,  # type: ignore
        lambda _: True, pass_bot=True,
        admin_users=admin_users_factory.filter())
