import asyncio
import telebot
import flask
from flask import jsonify, request, send_file, Response

from Classes.CryptoBot import cryptoPay_payment_updates
from Classes.YooKassa import yooKassa_payment_updates

from config_global import CRYPTOPAY_URL, PROD, YOOKASSA_URL, base_url, flask_port
from config_logger import logger

from callbacks.calculate import send_after_first_try
from callbacks.stats import edit_channel_post, edit_live_info, send_vote, send_week_stats

from initialize import bot
from db import db
from models import LiveInfo, LiveStats, LiveWait, SentMessages
from thread_tasks import run_thread


logger.info('INITIALIZE')
app = flask.Flask(__name__)
run_thread(bot)


@app.route(base_url + '/AAA', methods=['POST', 'GET'])
async def AAA():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(
            request.stream.read().decode('utf-8')
        )
        if update is None:
            flask.abort(403)

        asyncio.ensure_future(bot.process_new_updates([update]))

        return ''
    else:
        flask.abort(403)


# Payments WebHooks
@app.route(base_url + CRYPTOPAY_URL, methods=['POST', 'GET'])
async def cryptobot_updates():
    return await cryptoPay_payment_updates(bot, request)


@app.route(base_url + YOOKASSA_URL, methods=['POST', 'GET'])
async def yookassa_updates():
    return await yooKassa_payment_updates(bot, request)


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
async def vote_timeout():
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return Response(status=400)

    stat_id = request.args.get('stat_id')
    if stat_id is None or not stat_id.isnumeric():
        return Response(status=400)

    await send_vote(bot, int(stat_id))
    return Response(status=200)

@app.route(base_url + '/first_timeout', methods=['GET'])
async def first_timeout():
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return Response(status=400)

    user_id = request.args.get('user_id')
    if user_id is None or not user_id.isnumeric():
        return Response(status=400)

    try:
        await send_after_first_try(bot, int(user_id))
    except:
        return Response(status=400)
    return Response(status=200)

@app.route(base_url + '/stats_post', methods=['POST'])
async def stats_post():
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return Response(status=400)

    await send_week_stats(bot, is_new_week=True)

    return Response(status=200)

@app.route(base_url + '/calc_post', methods=['GET'])
async def calc_post():
    # access_token = db.get_access_token()
    # api_key = request.headers.get('tg-api-key')

    # if access_token is None or api_key is None or access_token != api_key:
    #     return Response(status=400)

    calc_id = request.args.get('calc_id')
    if calc_id is None or not calc_id.isnumeric():
        return Response(status=400)

    await edit_channel_post(bot, int(calc_id))

    return Response(status=200)

@app.route(base_url + '/live-info', methods=['POST'])
async def live_info():
    access_token = db.get_access_token()
    api_key = request.headers.get('tg-api-key')

    if access_token is None or api_key is None or access_token != api_key:
        return Response(status=400)

    res = request.get_json()

    messages = res.get('messages')
    data: list[dict] = res.get('data')
    wait: list[dict] = res.get('wait')
    canceled: list[dict] = res.get('canceled')

    live = (
        None if messages is None else SentMessages(**messages),
        [LiveInfo(**el) for el in data],
        [LiveWait(**el) for el in wait],
        [LiveWait(**el) for el in canceled],
        LiveStats(**res)
    )

    await edit_live_info(bot, live)

    return Response(status=200)

if PROD:
    from waitress import serve
    serve(app, host="127.0.0.1", port=flask_port, threads=5)
else:
    import _index  # type: ignore
    app.run(host='127.0.0.1', port=flask_port)
