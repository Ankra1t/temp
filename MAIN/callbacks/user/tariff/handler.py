from telebot import TeleBot
from telebot.types import CallbackQuery

from MAIN.callbacks.user.pages import send_tariffs_list_item
from initialize import pays, pays_banker
from config_logger import logger
from models import Invoice

from MAIN.callbacks import send_user_tariffs, send_user_main

from .filter import user_tariff_factory, UserTariffCallbackFilter
from .keyboards import (
    kb_bill_many, kb_bill_cryptobot
)


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = user_tariff_factory.parse(call.data)
    type = callback_data.get('type', '')
    target_id = callback_data.get('tariff_id', '')
    tariff_type = callback_data.get('tariff_type', '')
    page = int(callback_data.get('page', 0))

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'go_main':
        send_user_main(bot, call.message, user_id)

    if 'go_tariff' in type:
        del_mes = 'del' in type

        send_user_tariffs(bot, call.message, user_id, del_mes)

        if del_mes:
            bot.delete_message(chat_id, mes_id)

    if type == 'pay_tariff':
        tariff = pays.get_params_payservice_by_id(target_id)

        # Сообщение, что идет создание платежа
        edit_wait_mess = bot.send_message(
            call.message.chat.id,
            '⏳ Подготавливаем для вас возможные способы оплаты, подождите, пожалуйста ...'
        )
        bot.delete_message(chat_id, mes_id)

        if tariff is None:
            return

        # ------------ Оплата через CryptoBot Payments
        if True:
            # Формируем оплату через CryptoBot Payments
            try:
                for_client = "Оплатить " + tariff.name
                final_price = pays.check_discount_price(tariff)
                invoice_to_send: Invoice = pays.create_invoice(
                    tariff.currency, final_price, for_client)
            except Exception as e:
                logger.error(f'Ошибка в Pays.create_invoice [{e}]')

            logger.info(
                f'Получен чек от Cryptobot invoice_to_send [{invoice_to_send}]')

            # Формируем транзакцию от CryptoBot Payments для ожидания оплаты
            try:
                pays.set_transactions_for_wait(
                    user_id, invoice_to_send, tariff.id or 0)
                logger.info(
                    f'-----> Транзакция для оплаты через Криптобота удачно сохранена ждем платеж'
                )

            except Exception as e:
                logger.error(
                    f'Ошибка CryptoBot set_transactions_for_wait[{e}]'
                )

            # Отправить пользователю счет для оплаты со ссылкой
            show_price = '{} {}'.format(
                str(invoice_to_send.amount), invoice_to_send.asset)
            pay_link = invoice_to_send.pay_url
            pay_link1 = pay_link

        # ------------ Формируем оплату через BitBanker
        # Пока делаем целые
        final_price = int(pays_banker.check_discount_price(tariff))
        invoice_to_send_bb = None
        if final_price >= 50:

            try:
                for_client = "Оплатить " + tariff.name

                invoice_to_send_bb = pays_banker.create_invoice(
                    # asset, amount, description, payer, data_payments
                    tariff.currency, final_price, for_client, f'Пользователь id {user_id}')

            except Exception as e:
                logger.error(f'Ошибка в pays_banker.create_invoice [{e}]')

            if invoice_to_send_bb:
                logger.info(
                    f'Получен чек от BitBanker invoice_to_send [{invoice_to_send_bb}]')

                # Формируем транзакцию от BitBanker для ожидания оплаты
                try:
                    pays_banker.set_transactions_for_wait(
                        user_id, invoice_to_send_bb, tariff.id)
                    logger.info(
                        f'-----> Транзакция для оплаты через Криптобота удачно сохранена ждем платеж ')

                except Exception as e:
                    logger.error(
                        f'Ошибка pays_banker.set_transactions_for_wait[{e}]')

                # Отправить пользователю счет для оплаты со ссылкой
                show_price = '{} {}'.format(
                    str(invoice_to_send_bb.amount), invoice_to_send_bb.asset)
                pay_link2 = invoice_to_send_bb.pay_url

                # Отправляем сразу две кнопки оплаты
                bot.edit_message_text(
                    '❗️ Выберите удобный способ оплаты (регистрация не требуется)'.format(
                        tariff.name),
                    chat_id,
                    edit_wait_mess.message_id,
                    reply_markup=kb_bill_many(
                        show_price, pay_link1, pay_link2 or ''
                    )
                )

            else:
                bot.edit_message_text(
                    '❗️ После перехода в CryptoBot нажмите <b>\"ЗАПУСТИТЬ\"</b> и <b>оплатите счет</b>'.format(
                        tariff.name),
                    chat_id,
                    edit_wait_mess.message_id,
                    reply_markup=kb_bill_cryptobot(
                        show_price, pay_link1
                    )
                )

        else:
            bot.edit_message_text(
                '❗️ После перехода в CryptoBot нажмите <b>\"ЗАПУСТИТЬ\"</b> и <b>оплатите счет</b>'.format(
                    tariff.name),
                chat_id,
                edit_wait_mess.message_id,
                reply_markup=kb_bill_cryptobot(
                    show_price, pay_link1
                )
            )

    if type == 'get_tariff':
        send_tariffs_list_item(
            bot, call.message, user_id, tariff_type, page
        )

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(UserTariffCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        user_tariff=user_tariff_factory.filter()
    )
