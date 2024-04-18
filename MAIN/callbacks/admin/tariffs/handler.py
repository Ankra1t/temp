from telebot import TeleBot
from telebot.types import CallbackQuery

from MAIN.states import AdminTariffState
from CALCULATE.common.messages import msg_success_edit
from common.utils import delete_message, set_state_data
from db import db

from .filter import admin_tariffs_factory, AdminTariffsCallbackFilter
from .keyboards import kb_admin_tariff_add_type, kb_admin_tariffs_back, kb_admin_tariffs_list_back
from ..pages import send_admin_main, send_admin_tariffs, send_admin_tariffs_list_item


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    data = admin_tariffs_factory.parse(call.data)
    type = data.get('type', '')
    page = int(data.get('page', 0))
    tariff_id = int(data.get('id', -1))

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    if type == 'go_main':
        send_admin_main(bot, call.message, user_id)

    if 'go_tariffs' in type:
        is_del = 'del' in type
        if is_del:
            delete_message(bot, chat_id, mes_id)

        send_admin_tariffs(bot, call.message, user_id, is_del)

    if type == 'list':
        send_admin_tariffs_list_item(bot, call.message, user_id, page)

    if 'add' in type:
        if type == 'add':
            bot.edit_message_text(
                'Выберите тип нового тарифа:',
                chat_id, mes_id,
                reply_markup=kb_admin_tariff_add_type()
            )
        else:
            _, kind = type.split('+')

            bot.set_state(user_id, AdminTariffState.name, chat_id)
            set_state_data(bot, user_id, chat_id, {
                'action': 'create',
                'type_product': kind
            })
            bot.edit_message_text(
                'Введите название нового тарифа:', chat_id, mes_id,
                reply_markup=kb_admin_tariffs_back()
            )

    if 'delete' in type:
        if 'yes' in type:
            if db.deactive_price(tariff_id):
                delete_message(bot, chat_id, mes_id)
                bot.send_message(chat_id, msg_success_edit(user_id))
                send_admin_tariffs(bot, call.message, user_id, True)
        elif 'no' in type:
            send_admin_tariffs_list_item(bot, call.message, user_id, page)
        else:
            send_admin_tariffs_list_item(
                bot, call.message, user_id, page, 'delete')

    if type == 'on_off':
        tariff = db.get_price_by_id(tariff_id)
        if tariff is not None:
            new_switch_active = abs(tariff.switch_active - 1)
            if db.switch_tariff(tariff_id, new_switch_active):
                send_admin_tariffs_list_item(bot, call.message, user_id, page)

    if 'edit' in type:
        if type == 'edit':
            send_admin_tariffs_list_item(
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

            bot.set_state(user_id, state, chat_id)
            set_state_data(bot, user_id, chat_id, {
                'page': page,
                'tariff_id': tariff_id
            })
            delete_message(bot, chat_id, mes_id)
            bot.send_message(
                chat_id, text,
                reply_markup=kb_admin_tariffs_list_back(page)
            )

    if type == 'discount':
        tariff = db.get_price_by_id(tariff_id)
        if tariff is not None:
            bot.set_state(user_id, AdminTariffState.discount_percent, chat_id)
            set_state_data(bot, user_id, chat_id, {
                'tariff_id': tariff_id,
                'page': page
            })
            delete_message(bot, chat_id, mes_id)
            bot.send_message(
                chat_id, 'Введите размер скидки в процентах:',
                reply_markup=kb_admin_tariffs_list_back(page)
            )

    if type == 'discount_remove':
        if db.delete_price_discount(tariff_id):
            send_admin_tariffs_list_item(bot, call.message, user_id, page)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminTariffsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_tariffs=admin_tariffs_factory.filter())
