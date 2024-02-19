from datetime import datetime, timedelta
from gettext import find
from telebot import TeleBot
from telebot.types import Message

from common.utils import digit_accept, text_accept, set_state_data
from common.vars import DATE_FORMAT, PRINT_DATE_FROMAT


from MAIN.states import AdminTariffState

from db_new import db_new
from initialize import kb_inl_admin, tariff_manager, logger
from models import Discount, Price


def handle_name(message: Message, bot: TeleBot):
    name = text_accept(message)

    chat_id = message.chat.id
    user_id = message.from_user.id

    current_state = bot.get_state(user_id, chat_id)

    if name is None:
        bot.send_message(
            chat_id,
            'Введите название тарифа',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    if current_state == 'AdminTariffState:edit_field_name':
        with bot.retrieve_data(user_id, chat_id) as data:
            tariff_id = data.get('tariff_id')
            # tariff = db_new.get_price_by_id(data.get('tariff_id'))

        db_new.update_price_field('name', name, tariff_id)
        tariff = db_new.get_price_by_id(tariff_id)

        desc_template = tariff_manager.get_template_tariff_show_admin(tariff)
        bot.send_photo(chat_id, tariff.img, desc_template,
                       reply_markup=kb_inl_admin.kb_tariff_options(tariff_id))
        bot.send_message(
            chat_id, f'Тариф "{tariff.name}" с price {tariff.price} USDT изменен',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel()
        )

        bot.delete_state(user_id, chat_id)

    if current_state == 'AdminTariffState:name':
        set_state_data(bot, user_id, chat_id, {'name': name})
        bot.set_state(user_id, AdminTariffState.duration, chat_id)
        bot.send_message(
            chat_id, 'Введите кол-во дней действия тарифа',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())


def handle_duration(message: Message, bot: TeleBot):
    days = digit_accept(message, int)

    chat_id = message.chat.id
    user_id = message.from_user.id

    current_state = bot.get_state(user_id, chat_id)

    if days is None or days == 0:
        bot.send_message(
            chat_id, 'Введите количество дней более 0',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    if current_state == 'AdminTariffState:edit_field_duration':
        with bot.retrieve_data(user_id, chat_id) as data:
            tariff_id = data.get('tariff_id')

        db_new.update_price_field('duration_days', days, tariff_id)
        tariff = db_new.get_price_by_id(tariff_id)

        desc_template = tariff_manager.get_template_tariff_show_admin(tariff)
        bot.send_photo(chat_id, tariff.img, desc_template,
                       reply_markup=kb_inl_admin.kb_tariff_options(tariff_id))
        bot.send_message(
            chat_id, f'Тариф "{tariff.name}" с price {tariff.price} USDT изменен',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

        bot.delete_state(user_id, chat_id)

    if current_state == 'AdminTariffState:duration':
        set_state_data(bot, user_id, chat_id, {'duration': days})
        bot.set_state(user_id, AdminTariffState.price, chat_id)
        bot.send_message(
            chat_id, 'Стоимость нового тарифа в USDT',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())


def handle_price(message: Message, bot: TeleBot):
    price = digit_accept(message, int)

    chat_id = message.chat.id
    user_id = message.from_user.id

    current_state = bot.get_state(user_id, chat_id)

    if price is None or price == 0:
        bot.send_message(
            chat_id, 'Введите число более 0',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    if current_state == 'AdminTariffState:edit_field_price':
        with bot.retrieve_data(user_id, chat_id) as data:
            tariff_id = data.get('tariff_id')

        db_new.update_price_field('price', price, tariff_id)
        tariff = db_new.get_price_by_id(tariff_id)

        desc_template = tariff_manager.get_template_tariff_show_admin(tariff)
        bot.send_photo(chat_id, tariff.img, desc_template,
                       reply_markup=kb_inl_admin.kb_tariff_options(tariff_id))
        bot.send_message(
            chat_id, f'Тариф "{tariff.name}" с price {tariff.price} USDT изменен',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

        bot.delete_state(user_id, chat_id)

    if current_state == 'AdminTariffState:price':

        set_state_data(bot, user_id, chat_id, {'price': price})
        bot.set_state(user_id, AdminTariffState.image, chat_id)
        bot.send_message(
            chat_id, 'Постер (картинку) для нового тарифа',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())


def handle_image(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    current_state = bot.get_state(user_id, chat_id)

    if message.content_type != 'photo' or message.photo is None:
        bot.send_message(
            chat_id, 'Пожалуйста, отправьте картинку для тарифа',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    if current_state == 'AdminTariffState:edit_field_image':
        with bot.retrieve_data(user_id, chat_id) as data:
            tariff_id = data.get('tariff_id')

        db_new.update_price_field('img', message.photo[-1].file_id, tariff_id)
        tariff = db_new.get_price_by_id(tariff_id)

        desc_template = tariff_manager.get_template_tariff_show_admin(tariff)
        bot.send_photo(
            chat_id, tariff.img, desc_template,
            reply_markup=kb_inl_admin.kb_tariff_options(tariff_id)
        )
        bot.send_message(
            chat_id, f'Тариф "{tariff.name}" с price {tariff.price} USDT изменен',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel()
        )

        bot.delete_state(user_id, chat_id)

    if current_state == 'AdminTariffState:image':

        set_state_data(bot, user_id, chat_id, {
                       'image': message.photo[-1].file_id})
        bot.set_state(user_id, AdminTariffState.description, chat_id)
        bot.send_message(
            chat_id, 'Отправьте описание нового тарифа в виде текста',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())


def handle_description(message: Message, bot: TeleBot):
    description = text_accept(message)

    chat_id = message.chat.id
    user_id = message.from_user.id

    current_state = bot.get_state(user_id, chat_id)

    if description is None:
        bot.send_message(
            chat_id, 'Неправильно задан текст',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    if current_state == 'AdminTariffState:edit_field_description':
        with bot.retrieve_data(user_id, chat_id) as data:
            tariff_id = data.get('tariff_id')

        db_new.update_price_field('description', description, tariff_id)
        tariff = db_new.get_price_by_id(tariff_id)

        desc_template = tariff_manager.get_template_tariff_show_admin(tariff)
        bot.send_photo(
            chat_id, tariff.img, desc_template,
            reply_markup=kb_inl_admin.kb_tariff_options(tariff_id)
        )
        bot.send_message(
            chat_id, f'Тариф "{tariff.name}" с price {tariff.price} USDT изменен',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    if current_state == 'AdminTariffState:description':

        with bot.retrieve_data(user_id, chat_id) as data:
            name = data.get('name')
            duration = data.get('duration')
            price = data.get('price')
            image = data.get('image')
            type_product = data.get('type_product')

        tariff = Price(name, duration, price, 'USDT', None,
                       image, description, type_product=type_product)

        db_new.add_price(tariff)

        desc_template = tariff_manager.get_template_tariff_show_admin(tariff)
        bot.send_photo(chat_id, tariff.img, desc_template)

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
        chat_id, 'Введите дату окончания скидки в формате DD.MM.YY',
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
        fin_date_obj = datetime.strptime(discount_findate, '%d.%m.%y')
    except:
        bot.send_message(
            chat_id, 'Неправильно введена дата окончания скидки',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        tariff_id = data.get('discount_id')
        discount_percent = data.get('discount_percent')

    discount = Discount(percent=discount_percent, findate=fin_date_obj)
    tariff_manager.set_discount_tariff(tariff_id, discount)
    date_admin_show = fin_date_obj.strftime(PRINT_DATE_FROMAT)
    # date_admin_show = fin_date_obj.strftime('%d/%m/%Y')

    bot.send_message(
        chat_id, f'Тарифу id {tariff_id} добавлена скидка {discount.percent}% до {date_admin_show}',
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel())

    bot.delete_state(user_id, chat_id)


def handle_price_findate_count_days(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    days = digit_accept(message, int)

    if days is None or days == 0:
        bot.send_message(
            chat_id, 'Введите количество дней более 0',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return
    
    with bot.retrieve_data(user_id, chat_id) as data:
        tariff_id = data.get('tariff_id')

    price_findate_obj = datetime.now() + timedelta(days=days)

    findate_set_db = price_findate_obj.strftime(DATE_FORMAT)
    findate_show = price_findate_obj.strftime(PRINT_DATE_FROMAT)

    tariff_manager.set_findate_tariff(tariff_id, findate_set_db)

    bot.send_message(
        chat_id,
        f"Тариф id = {tariff_id} будет действовать до {findate_show} и потом автоматически отключится",
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel()
    )

    bot.delete_state(user_id, chat_id)

def handle_price_findate(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    price_findate = text_accept(message)

    try:
        price_findate_obj = datetime.strptime(price_findate, '%d.%m.%y')
    except Exception as e:
        price_findate_obj = None
        logger.error(f'Ошибка handle_price_findate [{e}]')

    if not price_findate or not price_findate_obj:
        bot.send_message(
            chat_id, 'Неправильно введена дата окончания тарифа (необходимо в <b>формате DD.MM.YY</b>)',
            reply_markup=kb_inl_admin.kb_tariffs_back_cancel())
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        tariff_id = data.get('tariff_id')

    findate_set_db = price_findate_obj.strftime(DATE_FORMAT)
    findate_show = price_findate_obj.strftime(PRINT_DATE_FROMAT)

    # Задаем дату окончания тарифа
    tariff_manager.set_findate_tariff(tariff_id, findate_set_db)

    bot.send_message(
        chat_id,
        f"Тариф id = {tariff_id} будет действовать до {findate_show} и потом автоматически отключится",
        reply_markup=kb_inl_admin.kb_tariffs_back_cancel()
    )

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

    reg_mes(handle_name, state=AdminTariffState.edit_field_name)
    reg_mes(handle_duration, state=AdminTariffState.edit_field_duration)
    reg_mes(handle_description, state=AdminTariffState.edit_field_description)
    reg_mes(handle_price, state=AdminTariffState.edit_field_price)
    reg_mes(handle_image, state=AdminTariffState.edit_field_image)

    reg_mes(handle_price_findate_count_days, state=AdminTariffState.price_findate_count_days)
    reg_mes(handle_price_findate, state=AdminTariffState.price_findate)
