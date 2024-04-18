from Classes.CryptoBot import cryptoPay_payment_updates
from Classes.YooKassa import yooKassa_payment_updates
import telebot
import flask
from flask import request

from config_logger import logger
from config_global import CRYPTOPAY_URL, PROD, YOOKASSA_URL, base_url, flask_port
from StartBot import bot
from CALCULATE.initialize import bot_calc


app = flask.Flask(__name__)


@app.route(base_url + '/AAA', methods=['POST', 'GET'])
def AAA():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(
            request.stream.read().decode('utf-8')
        )
        bot.process_new_updates([update])  # type: ignore

        return ''
    else:
        flask.abort(403)


@app.route(base_url + '/BBB', methods=['POST', 'GET'])
def BBB():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(
            request.stream.read().decode('utf-8')
        )
        bot_calc.process_new_updates([update])  # type: ignore

        return ''
    else:
        flask.abort(403)


# Payments WebHooks
@app.route(base_url + CRYPTOPAY_URL, methods=['POST', 'GET'])
def cryptobot_updates():
    print(f'{CRYPTOPAY_URL} request')
    return cryptoPay_payment_updates(request)


@app.route(base_url + YOOKASSA_URL, methods=['POST', 'GET'])
def yookassa_updates():
    print(f'{YOOKASSA_URL} request')
    return yooKassa_payment_updates(request)


if PROD:
    from waitress import serve
    serve(app, host="127.0.0.1", port=flask_port)
else:
    import _index  # type: ignore
    app.run(host='127.0.0.1', port=flask_port)
