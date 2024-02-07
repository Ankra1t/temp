from initialize import bot, kb_inl_user, pays, pays_banker, tariff_manager

from telebot import types

from cb_filters import client_action
from config_logger import logger

from models import Invoice, InvoiceBBanker


@bot.callback_query_handler(func=None, action=client_action.filter())
def client_action_callbacks(call: types.CallbackQuery):
    callback_data: dict = client_action.parse(callback_data=call.data)
    action, target_id = callback_data['action'], callback_data['id']
    # action, target_id, user_id = callback_data['action'], callback_data['id'], callback_data['user_id']

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    mes_id = call.message.id

    logger.info(f'Кнопка client callback_query ***{action}***')
    logger.info(f'Элемент client target_id ***{target_id}***')
    logger.info(f'Элемент client user_id ***{user_id}***')

    if action == 'pay_tariff':
        logger.info(f'-----> Действие ***{action}*** ')
        tariff = pays.get_params_payservice_by_id(target_id)

        # Сообщение, что идет создание платежа
        edit_wait_mess = bot.send_message(
            call.message.chat.id,
            '⏳ Подготавливаем для вас возможные способы оплаты, подождите, пожалуйста ... ')

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
                    user_id, invoice_to_send, tariff.id)
                logger.info(
                    f'-----> Транзакция для оплаты через Криптобота удачно сохранена ждем платеж ')

            except Exception as e:
                logger.error(
                    f'Ошибка CryptoBot set_transactions_for_wait[{e}]')

            # Отправить пользователю счет для оплаты со ссылкой
            show_price = '{} {}'.format(
                str(invoice_to_send.amount), invoice_to_send.asset)
            pay_link = invoice_to_send.pay_url
            pay_link1 = pay_link

        # ------------ Формируем оплату через BitBanker
        # Пока делаем целые
        final_price = int(pays_banker.check_discount_price(tariff))
        invoice_to_send_bb = None
        if final_price > 50 or final_price == 50:

            try:
                for_client = "Оплатить " + tariff.name

                invoice_to_send_bb = pays_banker.create_invoice(
                    # asset, amount, description, payer, data_payments
                    tariff.currency, final_price, for_client, f'Пользователь id {user_id}')

            except Exception as e:
                logger.error(f'Ошибка в pays_banker.create_invoice [{e}]')

            if invoice_to_send_bb:
                # if invoice_to_send_bb is None:
                #     return

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
                    reply_markup=kb_inl_user.kb_bill_many(
                        show_price, pay_link1, pay_link2
                    )
                )
                # bot.send_message(
                #     call.message.chat.id, '❗️ Выберите удобный способ оплаты (регистрация не требуется)'.format(tariff.name),
                #     reply_markup=kb_inl_user.kb_bill_many(
                #         show_price, pay_link1, pay_link2
                #     )
                # )

            else:
                bot.edit_message_text(
                    '❗️ После перехода в CryptoBot нажмите <b>\"ЗАПУСТИТЬ\"</b> и <b>оплатите счет</b>'.format(
                        tariff.name),
                    chat_id,
                    edit_wait_mess.message_id,
                    reply_markup=kb_inl_user.kb_bill(show_price, pay_link1)
                )
                # bot.send_message(
                #     call.message.chat.id, '❗️ После перехода в CryptoBot нажмите <b>\"ЗАПУСТИТЬ\"</b> и <b>оплатите счет</b>'.format(tariff.name),
                #     reply_markup=kb_inl_user.kb_bill(show_price, pay_link1)
                # )
                # bot.send_message(
                #     call.message.chat.id,
                #     '❗️ После перехода в CryptoBot нажмите <b>\"ЗАПУСТИТЬ\"</b> и <b>оплатите счет</b>',
                # )

        else:
            bot.edit_message_text(
                '❗️ После перехода в CryptoBot нажмите <b>\"ЗАПУСТИТЬ\"</b> и <b>оплатите счет</b>'.format(tariff.name),
                chat_id,
                edit_wait_mess.message_id,
                reply_markup=kb_inl_user.kb_bill(show_price, pay_link1)
            )
            # bot.send_message(
            #     call.message.chat.id, '❗️ После перехода в CryptoBot нажмите <b>\"ЗАПУСТИТЬ\"</b> и <b>оплатите счет</b>'.format(tariff.name),
            #     reply_markup=kb_inl_user.kb_bill(show_price, pay_link1)
            # )

    if action == 'tariffs_for_user_by_product':
        logger.info(f'-----> Действие ***{action}*** ')
        tariff_manager.tariff_list_show(call.message, product_id=target_id)
