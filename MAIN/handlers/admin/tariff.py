from datetime import datetime
from gettext import find
from telebot import TeleBot
from telebot.types import Message

from common.utils import digit_accept, text_accept, set_state_data

from MAIN.states import AdminTariffState

from db_new import db_new
from initialize import kb_inl_admin, tariff_manager
from models import Discount, Price


def handle_name(message: Message, bot: TeleBot):
    name = text_accept(message)

    chat_id = message.chat.id
    user_id = message.from_user.id

    if name is None:
        bot.send_message(
            chat_id,
            'Введите название тарифа',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    set_state_data(bot, user_id, chat_id, {'name': name})
    bot.set_state(user_id, AdminTariffState.duration, chat_id)
    bot.send_message(
        chat_id, 'Введите кол-во дней действия тарифа',
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel())


def handle_duration(message: Message, bot: TeleBot):
    days = digit_accept(message, int)

    chat_id = message.chat.id
    user_id = message.from_user.id

    if days is None or days == 0:
        bot.send_message(
            chat_id, 'Введите количество дней более 0',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    set_state_data(bot, user_id, chat_id, {'duration': days})
    bot.set_state(user_id, AdminTariffState.price, chat_id)
    bot.send_message(
        chat_id, 'Стоимость нового тарифа в USDT',
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel())


def handle_price(message: Message, bot: TeleBot):
    price = digit_accept(message, int)

    chat_id = message.chat.id
    user_id = message.from_user.id

    if price is None or price == 0:
        bot.send_message(
            chat_id, 'Введите число более 0',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    set_state_data(bot, user_id, chat_id, {'price': price})
    bot.set_state(user_id, AdminTariffState.image, chat_id)
    bot.send_message(
        chat_id, 'Постер (картинку) для нового тарифа',
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel())


def handle_image(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.content_type != 'photo' or message.photo is None:
        bot.send_message(
            chat_id, 'Пожалуйста, отправьте картинку для тарифа',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    set_state_data(bot, user_id, chat_id, {'image': message.photo[-1].file_id})
    bot.set_state(user_id, AdminTariffState.description, chat_id)
    bot.send_message(
        chat_id, 'Отправьте описание нового тарифа в виде текста',
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel())


def handle_description(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    description = text_accept(message)
    if description is None:
        bot.send_message(
            chat_id, 'Неправильно задан текст',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        name = data.get('name')
        duration = data.get('duration')
        price = data.get('price')
        image = data.get('image')

    tariff = Price(name, duration, price, 'USDT', None, image, description)

    db_new.add_price(tariff)

    desc_template = tariff_manager.get_template_tariff_show(tariff)
    bot.send_photo(chat_id, tariff.img, desc_template, "HTML")

    bot.send_message(
        chat_id, f'Тариф "{tariff.name}" с price {tariff.price} USDT создан',
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    bot.delete_state(user_id, chat_id)


def handle_discount_percent(message: Message, bot: TeleBot):
    discount_percent = digit_accept(message, int)

    chat_id = message.chat.id
    user_id = message.from_user.id

    if discount_percent is None or discount_percent < 0 or discount_percent > 100:
        bot.send_message(
            chat_id, 'Введите скидку в % от 0 до 100',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    set_state_data(bot, user_id, chat_id,
                   {'discount_percent': discount_percent})
    bot.set_state(user_id, AdminTariffState.discount_fin_date, chat_id)
    bot.send_message(
        chat_id, 'Введите дату окончания скидки в формате DD.MM.YYYY',
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel())


def handle_discount_fin_date(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    discount_findate = text_accept(message)
    if discount_findate is None:
        bot.send_message(
            chat_id, 'Неправильно введена дата окончания скидки',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    try:
        fin_date_obj = datetime.strptime(discount_findate, '%d.%m.%Y')
    except:
        bot.send_message(
            chat_id, 'Неправильно введена дата окончания скидки',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        tarrif_id = data.get('discount_id')
        discount_percent = data.get('discount_percent')

    discount = Discount(percent=discount_percent, findate=fin_date_obj)
    tariff_manager.set_discount_tariff(tarrif_id, discount)
    date_admin_show = fin_date_obj.strftime('%d/%m/%Y')

    bot.send_message(
        chat_id, f'Тарифу id {tarrif_id} добавлена скидка {discount.percent}% до {date_admin_show}',
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    bot.delete_state(user_id, chat_id)


def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_name, state=AdminTariffState.name)
    reg_mes(handle_duration, state=AdminTariffState.duration)
    reg_mes(handle_price, state=AdminTariffState.price)
    reg_mes(handle_image, state=AdminTariffState.image)
    reg_mes(handle_description, state=AdminTariffState.description)

    reg_mes(handle_discount_percent, state=AdminTariffState.discount_percent)
    reg_mes(handle_discount_fin_date, state=AdminTariffState.discount_fin_date)
