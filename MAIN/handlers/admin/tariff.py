from datetime import timedelta
from telebot import TeleBot
from telebot.types import Message

from common.utils import digit_accept, text_accept, set_state_data
from common.dt import get_datetime_by_str, get_str_by_datetime

from MAIN.callbacks import (
    kb_admin_tariffs_list_back, send_admin_tariffs_list_item, kb_admin_tariffs_back, send_admin_tariffs
)
from MAIN.states import AdminTariffState

from db import db
from models import Price


def handle_name(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    name = text_accept(message)
    if name is None:
        bot.send_message(
            chat_id, 'Введите название текстом:',
            reply_markup=back_keyboard
        )
        return

    if action == 'create':
        set_state_data(bot, user_id, chat_id, {'name': name})
        bot.set_state(user_id, AdminTariffState.price, chat_id)
        bot.send_message(
            chat_id, 'Введите цену тарифа:',
            reply_markup=back_keyboard
        )
    else:
        db.update_price_name(tariff_id, name)
        bot.delete_state(user_id, chat_id)
        send_admin_tariffs_list_item(
            bot, message, user_id, page, 'default', True
        )


def handle_price(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    price = digit_accept(message)
    if price is None:
        bot.send_message(
            chat_id, 'Введите цену числом:',
            reply_markup=back_keyboard
        )
        return

    if action == 'create':
        set_state_data(bot, user_id, chat_id, {'price': price})
        bot.set_state(user_id, AdminTariffState.duration, chat_id)
        bot.send_message(
            chat_id, 'Введите <b>кол-во дней</b> срока действия:',
            reply_markup=back_keyboard
        )
    else:
        db.update_price_price(tariff_id, price)
        bot.delete_state(user_id, chat_id)
        send_admin_tariffs_list_item(
            bot, message, user_id, page, 'default', True
        )


def handle_duration(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    duration = digit_accept(message, int)
    if duration is None:
        bot.send_message(
            chat_id, 'Введите срок действия числом:',
            reply_markup=back_keyboard
        )
        return

    if action == 'create':
        set_state_data(bot, user_id, chat_id, {'duration': duration})
        bot.set_state(user_id, AdminTariffState.image, chat_id)
        bot.send_message(
            chat_id, 'Отправьте картинку для тарифа:',
            reply_markup=back_keyboard
        )
    else:
        db.update_price_duration(tariff_id, duration)
        bot.delete_state(user_id, chat_id)
        send_admin_tariffs_list_item(
            bot, message, user_id, page, 'default', True
        )


def handle_image(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    if (message.content_type != 'photo') or (message.photo is None) or (len(message.photo) == 0):
        bot.send_message(
            chat_id, 'Отправьте картинку:',
            reply_markup=back_keyboard
        )
        return

    media_id = message.photo[0].file_id

    if action == 'create':
        set_state_data(bot, user_id, chat_id, {'image': media_id})
        bot.set_state(user_id, AdminTariffState.description, chat_id)
        bot.send_message(
            chat_id, 'Отправьте описание для тарифа:',
            reply_markup=back_keyboard
        )
    else:
        if bot.get_state(user_id, chat_id) == str(AdminTariffState.image_en):
            db.update_price_image_en(tariff_id, media_id)
        else:
            db.update_price_image(tariff_id, media_id)

        bot.delete_state(user_id, chat_id)
        send_admin_tariffs_list_item(
            bot, message, user_id, page, 'default', True
        )


def handle_description(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    with bot.retrieve_data(user_id, chat_id) as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    description = text_accept(message)
    if description is None:
        bot.send_message(
            chat_id, 'Введите описание текстом:',
            reply_markup=back_keyboard
        )
        return

    if action == 'create':
        with bot.retrieve_data(user_id, chat_id) as data:
            type_product = data.get('type_product', '')
            name = data.get('name', '')
            price = data.get('price', 0)
            duration = data.get('duration', 0)
            image = data.get('image')

        db.add_price(Price(
            id=0,
            name=name,
            description=description,
            duration=duration,
            price=price,
            currency='USDT',
            type_product=type_product,
            image=image,
            switch_active=1
        ))

        bot.send_message(chat_id, '✅ Тариф создан!')
        send_admin_tariffs(bot, message, user_id, True)
    else:
        db.update_price_description(tariff_id, description)
        bot.delete_state(user_id, chat_id)
        send_admin_tariffs_list_item(
            bot, message, user_id, page, 'default', True
        )


def handle_discount_percent(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    message.text = (message.text or '').replace('%', '')
    discount_percent = digit_accept(message, int)

    with bot.retrieve_data(user_id, chat_id) as data:
        page = data.get('page', 0)

    if discount_percent is None or discount_percent < 0 or discount_percent > 100:
        bot.send_message(
            chat_id, 'Введите скидку в % от 0 до 100',
            reply_markup=kb_admin_tariffs_list_back(page)
        )
        return

    set_state_data(
        bot, user_id, chat_id,
        {'discount_percent': discount_percent}
    )
    bot.set_state(user_id, AdminTariffState.discount_datetime, chat_id)
    bot.send_message(
        chat_id, 'Введите дату окончания скидки в формате ДД.ММ.ГГ ЧЧ:ММ',
        reply_markup=kb_admin_tariffs_list_back(page)
    )


def handle_discount_datetime(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    with bot.retrieve_data(user_id, chat_id) as data:
        discount_percent = data.get('discount_percent', 0)
        tariff_id = data.get('tariff_id', -1)
        page = data.get('page', 0)

    discount_findate = text_accept(message)
    if discount_findate is None:
        bot.send_message(
            chat_id, 'Введите дату и время текстом',
            reply_markup=kb_admin_tariffs_list_back(page)
        )
        return

    findate = get_datetime_by_str(discount_findate)
    if findate == False:
        bot.send_message(
            chat_id, 'Введите в формате - ДД.ММ.ГГ ЧЧ:ММ',
            reply_markup=kb_admin_tariffs_list_back(page)
        )
        return

    findate -= timedelta(hours=3)

    db.set_price_discount(tariff_id, discount_percent, findate)

    tariff = db.get_price_by_id(tariff_id)
    name = tariff.name if tariff is not None else tariff_id

    bot.send_message(
        chat_id,
        f'✅ Тарифу "{name}" добавлена скидка {discount_percent}% до {get_str_by_datetime(findate)}',
        reply_markup=kb_admin_tariffs_list_back(page)
    )
    send_admin_tariffs_list_item(
        bot, message, user_id, page, 'default', True
    )

    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_name, state=AdminTariffState.name)
    reg_mes(handle_price, state=AdminTariffState.price)
    reg_mes(handle_duration, state=AdminTariffState.duration)
    reg_mes(handle_image, state=AdminTariffState.image)
    reg_mes(handle_image, state=AdminTariffState.image_en)
    reg_mes(handle_description, state=AdminTariffState.description)

    reg_mes(handle_discount_percent, state=AdminTariffState.discount_percent)
    reg_mes(handle_discount_datetime, state=AdminTariffState.discount_datetime)
