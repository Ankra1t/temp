import telebot
import flask
from flask import request, Response

from config_logger import logger
from config_global import CRYPTOPAY_URL, BITBANKER_URL
from StartBot import bot, pays, pays_banker
from CALCULATE.initialize import bot_calc
# from NOTICE.bot_Notification import *
# from NOTICE.PostGresSQL_db import Database


logger.info(f' * * * * * Logging is Start Now * * * * * ')

app = flask.Flask(__name__)
base_url = '/_bots'

# Тестовый запрос
@app.route(base_url, methods=['POST', 'GET'])
def home():
    print(f'request.headers ')
    print(request.headers)
    print(f'request ')
    print(request)
    logger.info(f'Кто-то проверил работу сервера _bots')
    return "Hello!! server linux bot is WORK![" + base_url + '/AAA' + ']'


@app.route(base_url + '/AAA', methods=['POST', 'GET'])
def AAA():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(
            request.stream.read().decode('utf-8'))
        bot.process_new_updates([update]) # type: ignore
        logger.info(f'Пришел Update Telegram на [/AAA]')

        return ''
    else:
        flask.abort(403)
    if request.method == 'POST':
        return Response('ok', status=200)
    else:
        return " "


@app.route(base_url + '/BBB', methods=['POST', 'GET'])
def BBB():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(
            request.stream.read().decode('utf-8'))
        bot_calc.process_new_updates([update]) # type: ignore
        logger.info(f'Пришел Update Telegram на [/BBB]')
        print(f'Telegram sent on /BBB request ')
        print(request)
        print(request.stream.read().decode('utf-8'))
        return ''
    else:
        flask.abort(403)
    if request.method == 'POST':
        return Response('ok', status=200)
    else:
        return " "


# @app.route(base_url+'/CCC', methods=['POST', 'GET'])
# def CCC():
#     if request.headers.get('content-type') == 'application/json':
#         update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
#         bot_not.process_new_updates([update])
#         logger.info(f'Пришел Update Telegram на [/CCC]')

#         print(f'Telegram sent on /CCC request ')
#         print(request)
#         print(request.stream.read().decode('utf-8'))
#         return ''
#     else:
#         flask.abort(403)
#     if request.method == 'POST':
#         return Response('ok', status=200)
#     else:
#         return " "


# ======================= // ANCHOR WebHook Connect
@app.route(base_url+CRYPTOPAY_URL, methods=['POST', 'GET'])
def cryptobot_updates():
    # if request.headers.get('content-type') == 'application/json':
    print(f'Cryptobot sent on {CRYPTOPAY_URL} request ')
    print(request)
    return pays.get_updates(request)
#     # if not Pays.get_updates(request):
#         # flask.abort(403)


# ======================= // ANCHOR WebHook Connect BITBANKER
@app.route(base_url+BITBANKER_URL, methods=['POST', 'GET'])
def bitbanker_updates():
    # if request.headers.get('content-type') == 'application/json':
    print(f'BitBanker sent on {BITBANKER_URL} request ')
    print(request)
    return pays_banker.get_updates(request)
    # if not Pays.get_updates(request):
        # flask.abort(403)

app.run(host='127.0.0.1', port=5000, debug=True)
