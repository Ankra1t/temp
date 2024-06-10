import json
import telebot
import flask
from flask import jsonify, request, send_file

from Classes.CryptoBot import cryptoPay_payment_updates
from Classes.YooKassa import yooKassa_payment_updates

from config_global import CRYPTOPAY_URL, PROD, YOOKASSA_URL, base_url, flask_port
from config_logger import logger

from MAIN.initialize import bot
from thread_tasks import run_thread


logger.info('INITIALIZE')
app = flask.Flask(__name__)
run_thread(bot)


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


# Payments WebHooks
@app.route(base_url + CRYPTOPAY_URL, methods=['POST', 'GET'])
def cryptobot_updates():
    return cryptoPay_payment_updates(bot, request)


@app.route(base_url + YOOKASSA_URL, methods=['POST', 'GET'])
def yookassa_updates():
    return yooKassa_payment_updates(bot, request)


@app.route(base_url + '/icon.png', methods=['GET'])
def get_icon():
    return send_file('src/img/icon.png', mimetype='image/png')


@app.route(base_url + '/manifest.json', methods=['GET'])
def get_ton_manifest():
    return jsonify({
        "url": f"https://t.me/{bot.get_me().username}",
        "name": "Calc",
        "iconUrl": f"{request.url_root}{base_url}/icon.png",
        "1": request.url,
        "2": request.remote_addr,
        "3": request.host_url,
    })


if PROD:
    from waitress import serve
    serve(app, host="127.0.0.1", port=flask_port, threads=5)
else:
    import _index  # type: ignore
    app.run(host='127.0.0.1', port=flask_port)
