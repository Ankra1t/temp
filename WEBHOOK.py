import telebot
import flask
from flask import jsonify, request, send_file, Response

from CALCULATE.callbacks.calculate.handler import send_after_first_try
from CALCULATE.callbacks.stats.handler import send_vote, send_week_stats
from Classes.CryptoBot import cryptoPay_payment_updates
from Classes.YooKassa import yooKassa_payment_updates

from config_global import CRYPTOPAY_URL, PROD, YOOKASSA_URL, base_url, flask_port
from config_logger import logger

from MAIN.initialize import bot
from db import db
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
        # "url": f"https://t.me/{bot.get_me().username}",
        "url": "https://github.com/XaBbl4/pytonconnect",
        "name": "Calc",
        "iconUrl": "https://profmarkets.ai/_prodbots/icon.png",
    })

@app.route(base_url + '/vote_timeout', methods=['GET'])
def vote_timeout():
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return Response(status=400)

    stat_id = request.args.get('stat_id')
    if stat_id is None or not stat_id.isnumeric():
        return Response(status=400)

    send_vote(bot, int(stat_id))
    return Response(status=200)

@app.route(base_url + '/first_timeout', methods=['GET'])
def first_timeout():
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return Response(status=400)

    user_id = request.args.get('user_id')
    if user_id is None or not user_id.isnumeric():
        return Response(status=400)

    send_after_first_try(bot, int(user_id))
    return Response(status=200)

@app.route(base_url + '/stats_post', methods=['POST'])
def stats_post():
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return Response(status=400)

    send_week_stats(bot, True)

    return Response(status=200)

if PROD:
    from waitress import serve
    serve(app, host="127.0.0.1", port=flask_port, threads=5)
else:
    import _index  # type: ignore
    app.run(host='127.0.0.1', port=flask_port)
