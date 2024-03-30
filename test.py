import ast
from datetime import datetime, timedelta, timezone
from db import db
from initialize import bot

# azatFa  id 156045434
# ankrait id 6919899538

# db.delete_calculator_user(156045434)
# db.add_worker(156045434, 1)
# db.del_worker(156045434)

# print(db.get_access_token())


# db.add_user(-1, 'asd', 0)
# db.del_user(-1)

# db.curs.execute("SELECT * FROM tgbotusers")
# print(db.curs.fetchall())

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
# query += f"ORDER BY u.created_at {'ASC' if filter == 'old' else 'DESC'} "
# query += f", u.id ASC "
# query += "LIMIT %s OFFSET %s "

# print(query)

# print(
#     'SELECT u.id, u.id_telegram, u.username_tg, tu.refer_id, u.ban, u.created_at '
#     'FROM users as u LEFT JOIN tgbotusers as tu ON u.id = tu.user_id '
#     'WHERE u.ban = 0 '
#     'AND (SELECT COUNT (*) FROM subscribes as sub WHERE sub.tg_user_id = u.id_telegram) >= %s '
#     'AND (SELECT COUNT (*) FROM subscribes as sub WHERE sub.tg_user_id = u.id_telegram AND sub.avtive = 1) > 0 '
# )
