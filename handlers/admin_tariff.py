from datetime import timedelta
from telebot.async_telebot import AsyncTeleBot

from db import db
from models import Price, Message, StateContext

from common.utils import digit_accept, text_accept
from common.dt import get_datetime_by_str, get_str_by_datetime

from keyboards.admin_tariffs import (
    kb_admin_tariffs_list_back, kb_admin_tariffs_back
)

from states.admin_tariff import AdminTariffState
from pages.admin import send_admin_tariffs, send_admin_tariffs_list_item



async def handle_name(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    async with state.data() as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    name = text_accept(message)
    if name is None:
        await bot.send_message(
            chat_id, 'Введите название текстом:',
            reply_markup=back_keyboard
        )
        return

    if action == 'create':
        await state.add_data(name=name)
        await state.set(AdminTariffState.price)
        await bot.send_message(
            chat_id, 'Введите цену тарифа:',
            reply_markup=back_keyboard
        )
    else:
        db.update_price_name(tariff_id, name)
        await state.delete()
        await send_admin_tariffs_list_item(
            bot, message, page, 'default', True
        )


async def handle_price(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    async with state.data() as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    price = digit_accept(message)
    if price is None:
        await bot.send_message(
            chat_id, 'Введите цену числом:',
            reply_markup=back_keyboard
        )
        return

    if action == 'create':
        await state.add_data(price=price)
        await state.set(AdminTariffState.duration)
        await bot.send_message(
            chat_id, 'Введите <b>кол-во дней</b> срока действия:',
            reply_markup=back_keyboard
        )
    else:
        db.update_price_price(tariff_id, price)
        await state.delete()
        await send_admin_tariffs_list_item(
            bot, message, page, 'default', True
        )


async def handle_duration(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    async with state.data() as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    duration = digit_accept(message, int)
    if duration is None:
        await bot.send_message(
            chat_id, 'Введите срок действия числом:',
            reply_markup=back_keyboard
        )
        return

    if action == 'create':
        await state.add_data(duration=duration)
        await state.set(AdminTariffState.image)
        await bot.send_message(
            chat_id, 'Отправьте картинку для тарифа:',
            reply_markup=back_keyboard
        )
    else:
        db.update_price_duration(tariff_id, duration)
        await state.delete()
        await send_admin_tariffs_list_item(
            bot, message, page, 'default', True
        )


async def handle_image(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    async with state.data() as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    if (message.content_type != 'photo') or (message.photo is None) or (len(message.photo) == 0):
        await bot.send_message(
            chat_id, 'Отправьте картинку:',
            reply_markup=back_keyboard
        )
        return

    media_id = message.photo[0].file_id

    if action == 'create':
        await state.add_data(image=media_id)
        await state.set(AdminTariffState.description)
        await bot.send_message(
            chat_id, 'Отправьте описание для тарифа:',
            reply_markup=back_keyboard
        )
    else:
        if (await state.get()) == str(AdminTariffState.image_en):
            db.update_price_image_en(tariff_id, media_id)
        else:
            db.update_price_image(tariff_id, media_id)

        await state.delete()
        await send_admin_tariffs_list_item(
            bot, message, page, 'default', True
        )


async def handle_description(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    async with state.data() as data:
        action = data.get('action', '')
        page = data.get('page', 0)
        tariff_id = data.get('tariff_id', -1)

    if action == 'create':
        back_keyboard = kb_admin_tariffs_back()
    else:
        back_keyboard = kb_admin_tariffs_list_back(page)

    description = text_accept(message)
    if description is None:
        await bot.send_message(
            chat_id, 'Введите описание текстом:',
            reply_markup=back_keyboard
        )
        return

    if action == 'create':
        async with state.data() as data:
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
            switch_active=True
        ))

        await bot.send_message(chat_id, '✅ Тариф создан!')
        await send_admin_tariffs(bot, message, state, True)
    else:
        db.update_price_description(tariff_id, description)
        await state.delete()
        await send_admin_tariffs_list_item(
            bot, message, page, 'default', True
        )


async def handle_discount_percent(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id

    message.text = (message.text or '').replace('%', '')
    discount_percent = digit_accept(message, int)

    async with state.data() as data:
        page = data.get('page', 0)

    if discount_percent is None or discount_percent < 0 or discount_percent > 100:
        await bot.send_message(
            chat_id, 'Введите скидку в % от 0 до 100',
            reply_markup=kb_admin_tariffs_list_back(page)
        )
        return

    await state.add_data(
        discount_percent=discount_percent
    )
    await state.set(AdminTariffState.discount_datetime)
    await bot.send_message(
        chat_id, 'Введите дату окончания скидки в формате ДД.ММ.ГГ ЧЧ:ММ',
        reply_markup=kb_admin_tariffs_list_back(page)
    )


async def handle_discount_datetime(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    async with state.data() as data:
        discount_percent = data.get('discount_percent', 0)
        tariff_id = data.get('tariff_id', -1)
        page = data.get('page', 0)

    discount_findate = text_accept(message)
    if discount_findate is None:
        await bot.send_message(
            chat_id, 'Введите дату и время текстом',
            reply_markup=kb_admin_tariffs_list_back(page)
        )
        return

    findate = get_datetime_by_str(discount_findate)
    if findate == False:
        await bot.send_message(
            chat_id, 'Введите в формате - ДД.ММ.ГГ ЧЧ:ММ',
            reply_markup=kb_admin_tariffs_list_back(page)
        )
        return

    findate -= timedelta(hours=3)

    db.set_price_discount(tariff_id, discount_percent, findate)

    tariff = db.get_price_by_id(tariff_id)
    name = tariff.name if tariff is not None else tariff_id

    await bot.send_message(
        chat_id,
        f'✅ Тарифу "{name}" добавлена скидка {discount_percent}% до {get_str_by_datetime(findate)}',
        reply_markup=kb_admin_tariffs_list_back(page)
    )
    await send_admin_tariffs_list_item(
        bot, message, page, 'default', True
    )

    await state.delete()


def registration(bot: AsyncTeleBot):
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
