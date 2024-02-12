from datetime import datetime, timedelta, timezone
from db_new import db_new

# azatFa  id 156045434
# ankrait id 6919899538

# db_new.delete_calculator_user(156045434)
# db_new.add_worker(156045434, 'azatFa', 1)
# db_new.del_worker(156045434)

# print(db_new.get_access_token())


# db_new.add_user(-1, 'asd', 0)
# db_new.del_user(-1)

# a = db_new.get_user_by_tg_id(-1)
# dt: datetime = a[1]

# if a is not None:
#     dt = a.date_time or datetime.now()
#
# data = db_new.get_all_users()
# print(data)

# db_new.curs.execute("SELECT * FROM tgbotusers")
# print(db_new.curs.fetchall())

# forexes = [{"pair": "AUD/CAD", "price": "0", "help_pair": "USD/CAD"},
#            {"pair": "AUD/CHF", "price": "0", "help_pair": "USD/CHF"},
#            {"pair": "AUD/JPY", "price": "0", "help_pair": "USD/JPY"},
#            {"pair": "CAD/CHF", "price": "0", "help_pair": "USD/CHF"},
#            {"pair": "CAD/JPY", "price": "0", "help_pair": "USD/JPY"},
#            {"pair": "CHF/JPY", "price": "0", "help_pair": "USD/JPY"},
#            {"pair": "EUR/AUD", "price": "0", "help_pair": "AUD/USD"},
#            {"pair": "EUR/CAD", "price": "0", "help_pair": "USD/CAD"},
#            {"pair": "EUR/CHF", "price": "0", "help_pair": "USD/CHF"},
#            {"pair": "EUR/GBP", "price": "0", "help_pair": "GBP/USD"},
#            {"pair": "EUR/JPY", "price": "0", "help_pair": "USD/JPY"},
#            {"pair": "EUR/NZD", "price": "0", "help_pair": "NZD/USD"},
#            {"pair": "GBP/AUD", "price": "0", "help_pair": "AUD/USD"},
#            {"pair": "GBP/CAD", "price": "0", "help_pair": "USD/CAD"},
#            {"pair": "GBP/CHF", "price": "0", "help_pair": "USD/CHF"},
#            {"pair": "GBP/JPY", "price": "0", "help_pair": "USD/JPY"},
#            {"pair": "GBP/NZD", "price": "0", "help_pair": "NZD/USD"},
#            {"pair": "NZD/CAD", "price": "0", "help_pair": "USD/CAD"},
#            {"pair": "NZD/CHF", "price": "0", "help_pair": "USD/CHF"},
#            {"pair": "NZD/JPY", "price": "0", "help_pair": "USD/JPY"},
#            {"pair": "NZD/USD", "price": "0.62625", "help_pair": ""},
#            {"pair": "GBP/USD", "price": "1.2936", "help_pair": ""},
#            {"pair": "EUR/USD", "price": "1.12044", "help_pair": ""},
#            {"pair": "AUD/USD", "price": "0.677", "help_pair": ""},
#            {"pair": "USD/JPY", "price": "139.608", "help_pair": ""},
#            {"pair": "USD/CHF", "price": "0.85793", "help_pair": ""},
#            {"pair": "USD/CAD", "price": "1.31632", "help_pair": ""},
#            {"pair": "USD/RUB", "price": "91.9445", "help_pair": ""}]

# query = (
#     'SELECT u.id, u.id_telegram, u.username_tg, tu.refer_id, u.ban, u.created_at  '
#     'FROM users as u LEFT JOIN tgbotusers as tu ON u.id = tu.user_id '
# )
# # if filter == 'by_paid':
# #     query += 'INNER JOIN subscribes ON users.id = subscribes.user_id '
# #     query += 'WHERE subscribes.active = 1 '
# query += f"ORDER BY u.created_at {'ASC' if filter == 'by_date_old' else 'DESC'} "
# query += f", u.id ASC "
# query += "LIMIT %s OFFSET %s "

# print(query)

# db_new.curs.execute('UPDATE users SET created_at = %s WHERE id <= 14',
#                     (datetime(2023, 8, 10, 5, 54),))
# db_new.connection.commit()

print(int(False))

# print(
#     'SELECT u.id, u.id_telegram, u.username_tg, tu.refer_id, u.ban, u.created_at '
#     'FROM users as u LEFT JOIN tgbotusers as tu ON u.id = tu.user_id '
#     'WHERE u.ban = 0 '
#     'AND (SELECT COUNT (*) FROM subscribes as sub WHERE sub.tg_user_id = u.id_telegram) >= %s '
#     'AND (SELECT COUNT (*) FROM subscribes as sub WHERE sub.tg_user_id = u.id_telegram AND sub.avtive = 1) > 0 '
# )

################################################################################################
# if user_role == 0:
#     if message.text == 'Купить':
#         subscribe_name = 'Подписка на месяц на сигналы'

#         try:
#             subscribe = pays.get_params_payservice(subscribe_name)
#         except Exception as e:
#             logger.error(f'Ошибка в get_params_payservice [{e}]')

#         try:
#             for_client = "Услуга " + subscribe['sub_name']
#             invoice_to_send: Invoice = pays.create_invoice(subscribe['currency'], subscribe['amount'],
#                                                            for_client)
#         except Exception as e:
#             logger.error(f'Ошибка в Pays.create_invoice [{e}]')

#         logger.info(
#             f'Получен чек от Cryptobot invoice_to_send [{invoice_to_send}]')

#         # Формируем транзакцию для ожидания оплаты
#         try:
#             pays.set_transactions_for_wait(
#                 message, invoice_to_send, subscribe['price_id'])
#             logger.info(
#                 f'-----> Транзакция удачно сохранена ждем платеж ')

#         except Exception as e:
#             logger.error(f'Ошибка set_transactions_for_wait[{e}]')

#         # Отправить пользователю счет для оплаты со ссылкой
#         show_price = '{} {}'.format(
#             str(invoice_to_send.amount), invoice_to_send.asset)
#         pay_link = invoice_to_send.pay_url

#         bot.send_message(message.chat.id, text='{}'.format(invoice_to_send.description),
#                          reply_markup=kb_users_bill(show_price, pay_link))
