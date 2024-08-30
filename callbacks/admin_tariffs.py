from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from states.admin_tariff import AdminTariffState
from common.utils import delete_message, get_lang, set_state_data
from db import db

from messages.common import msg_success_edit
from pages.admin import send_admin_main, send_admin_tariffs, send_admin_tariffs_list_item

from keyboards.admin_tariffs import (
    admin_tariffs_factory, AdminTariffsCallbackFilter,
    kb_admin_tariff_add_type, kb_admin_tariffs_back, kb_admin_tariffs_list_back
)


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot):
    data = admin_tariffs_factory.parse(call.data)
    type = data.get('type', '')
    page = int(data.get('page', 0))
    tariff_id = int(data.get('id', -1))

    user_id = call.from_user.id
    lang = get_lang(user_id)

    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'go_main':
        await send_admin_main(bot, call.message, user_id)

    if 'go_tariffs' in type:
        is_del = 'del' in type
        if is_del:
            await delete_message(bot, chat_id, mes_id)

        await send_admin_tariffs(bot, call.message, user_id, is_del)

    if type == 'list':
        await send_admin_tariffs_list_item(bot, call.message, user_id, page)

    if 'add' in type:
        if type == 'add':
            await bot.edit_message_text(
                'Выберите тип нового тарифа:',
                chat_id, mes_id,
                reply_markup=kb_admin_tariff_add_type()
            )
        else:
            _, kind = type.split('+')

            await bot.set_state(user_id, AdminTariffState.name, chat_id)
            await set_state_data(bot, user_id, chat_id, {
                'action': 'create',
                'type_product': kind
            })
            await bot.edit_message_text(
                'Введите название нового тарифа:', chat_id, mes_id,
                reply_markup=kb_admin_tariffs_back()
            )

    if 'delete' in type:
        if 'yes' in type:
            if db.deactive_price(tariff_id):
                await delete_message(bot, chat_id, mes_id)
                await bot.send_message(chat_id, msg_success_edit(lang))
                await send_admin_tariffs(bot, call.message, user_id, True)
        elif 'no' in type:
            await send_admin_tariffs_list_item(bot, call.message, user_id, page)
        else:
            await send_admin_tariffs_list_item(
                bot, call.message, user_id, page, 'delete')

    if type == 'on_off':
        tariff = db.get_price_by_id(tariff_id)
        if tariff is not None:
            if db.switch_tariff(tariff_id, not tariff.switch_active):
                await send_admin_tariffs_list_item(bot, call.message, user_id, page)

    if 'edit' in type:
        if type == 'edit':
            await send_admin_tariffs_list_item(
                bot, call.message, user_id, page, 'edit'
            )
        else:
            state = ''
            if 'name' in type:
                state = AdminTariffState.name
                text = 'Введите новое название тарифа:'
            elif 'price' in type:
                state = AdminTariffState.price
                text = 'Введите новую цену тарифа:'
            elif 'duration' in type:
                state = AdminTariffState.duration
                text = 'Введите новый срок действия (в днях) тарифа:'
            elif 'description' in type:
                state = AdminTariffState.description
                text = 'Введите новое описание тарифа:'
            elif 'image' in type:
                state = AdminTariffState.image
                text = 'Отправьте новую картинку тарифа:'
            elif 'img_en' in type:
                state = AdminTariffState.image_en
                text = 'Отправьте картинку на английском для тарифа:'
            elif 'findate' in type:
                state = ''

            await bot.set_state(user_id, state, chat_id)
            await set_state_data(bot, user_id, chat_id, {
                'page': page,
                'tariff_id': tariff_id
            })
            await delete_message(bot, chat_id, mes_id)
            await bot.send_message(
                chat_id, text,
                reply_markup=kb_admin_tariffs_list_back(page)
            )

    if type == 'discount':
        tariff = db.get_price_by_id(tariff_id)
        if tariff is not None:
            await bot.set_state(user_id, AdminTariffState.discount_percent, chat_id)
            await set_state_data(bot, user_id, chat_id, {
                'tariff_id': tariff_id,
                'page': page
            })
            await delete_message(bot, chat_id, mes_id)
            await bot.send_message(
                chat_id, 'Введите размер скидки в процентах:',
                reply_markup=kb_admin_tariffs_list_back(page)
            )

    if type == 'discount_remove':
        if db.delete_price_discount(tariff_id):
            await send_admin_tariffs_list_item(bot, call.message, user_id, page)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminTariffsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback, # type: ignore
        lambda _: True, pass_bot=True,
        admin_tariffs=admin_tariffs_factory.filter())
