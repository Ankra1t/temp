from datetime import datetime, timedelta
from db import db

# azatFa  id 156045434
# ankrait id 6919899538

# db.delete_calculator_user(156045434)
db.add_worker(156045434, 'azatFa', 1)
# db.del_worker(156045434)
# db.curs.execute('DELETE FROM users')
# db.connection.commit()

# a = datetime.now()

# print(a.time().isoformat('minutes'))

# arr = 'a'
# print(arr)
# a, b = arr.split('_')
# print(a)
# print(.0)


# query = ' '.join((
#         'CREATE TABLE posts (',
#         'id INTEGER PRIMARY KEY AUTOINCREMENT,',
#         'content TEXT NOT NULL,',
#         'mes_type VARCHAR(20) DEFAULT "text",',
#         'direct VARCHAR(20) DEFAULT "Всем",',
#         'media TEXT NULL,',
#         'date_time TIMESTAMP NOT NULL,',
#         'name TEXT NULL,',
#         'open_price FLOAT NULL,',
#         'stop_loss FLOAT NULL,',
#         'ticker VARCHAR(20) NULL',
#         ')',
# ))
# db.curs.execute(query)
# db.connection.commit()

db.curs.execute('DELETE FROM users WHERE id < 1000')
db.connection.commit()

for i in range(1, 30):
        query = (
                'INSERT INTO users(id, username, refer, count_sub, count_days, pay_money, balance, created_at) '
                'VALUES(?, ?, ?, 0, 0, 0, 0, ?)'
        )
        params = (i, f'andww{i}', 0, datetime.now() - timedelta(days=i))

        db.curs.execute(query, params)
        db.connection.commit()

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
#                          parse_mode="HTML", reply_markup=kb_users_bill(show_price, pay_link))
