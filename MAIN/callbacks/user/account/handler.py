from telebot import TeleBot
from telebot.types import CallbackQuery

from db import db

from .keyboards import kb_user_referral, kb_user_referral_list
from .filter import user_account_factory, UserAccountCallbackFilter

from MAIN.states import UserAccountState
from MAIN.callbacks import send_user_account, send_user_main
from MAIN.common.messages import msg_referral


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = user_account_factory.parse(call.data)
    type = callback_data.get('type') or ''

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    # цена входа
    #

    if type == 'purchases':
        # if type == 'purchases' or type == 'buy_month':
        purchases_list = db.get_purchases_by_user(user_id)
        bot.edit_message_text(
            '<b>--- Мои покупки</b>', chat_id, mes_id
        )

        if len(purchases_list) == 0:
            bot.send_message(
                chat_id,
                '<b>- - - Рекомендации:</b>'
            )
            bot.send_message(
                chat_id,
                'не куплено'
            )
            bot.send_message(
                chat_id,
                '<b>- - - Калькулятор:</b>')
            bot.send_message(
                chat_id,
                'не куплено'
            )
        else:

            product_list = {'signals': [], 'calc': []}

            template_buy_goods = """
                🛍 Покупка <b>{}</b> за {} {}
                дата {}
                            """

            # Сортируем услуги по продуктам
            for i in range(0, len(purchases_list)):
                purchase = purchases_list[i]
                date_buy = purchase.payment_date if purchase.payment_date else purchase.create_date
                purchase_show = template_buy_goods.format(purchase.price_name,
                                                          purchase.real_sum,
                                                          purchase.currency,
                                                          date_buy
                                                          )
                if purchase.type_product == 'calc':
                    product_list['calc'].append(purchase_show)
                if purchase.type_product == 'signals':
                    product_list['signals'].append(purchase_show)

            bot.send_message(
                chat_id,
                '<b>- - -Рекомендации:</b>'
            )
            if len(product_list['signals']):
                for i in range(0, len(product_list['signals'])):
                    bot.send_message(
                        chat_id,
                        product_list['signals'][i]
                    )
            else:
                bot.send_message(
                    chat_id,
                    'не куплено'
                )

            bot.send_message(
                chat_id,
                '<b>- - -Калькулятор:</b>'
            )
            if len(product_list['calc']):
                for i in range(0, len(product_list['calc'])):
                    bot.send_message(
                        chat_id,
                        product_list['calc'][i]
                    )
            else:
                bot.send_message(
                    chat_id, 'не куплено'
                )

    if type == 'main':
        send_user_main(bot, call.message, user_id)

    if type == 'back':
        send_user_account(bot, call.message, user_id)

    if type == 'referral':
        referals = db.get_user_referals(user_id)
        count_ref = len(referals)
        intext = msg_referral(count_ref, bot.get_me().username, user_id)

        bot.send_message(
            chat_id, text=intext,
            reply_markup=kb_user_referral()
        )

    if type == 'referral_list':
        referals = db.get_user_referals(user_id)
        res = ''
        if len(referals) != 0:
            for i in range(0, len(referals)):
                res += f'\nНик: {referals[i].username}\nВсего потратил: {referals[i].username}'
        else:
            res = "К сожалению, у вас нет рефералов 😔\n<b>Отправьте</b> свой реферальную ссылку друзьями, чтобы это исправить 😉"
        bot.send_message(
            chat_id, res, reply_markup=kb_user_referral_list()
        )

    if type == 'password':
        bot.edit_message_text(
            'Введите новый пароль:', chat_id, mes_id
        )
        bot.set_state(user_id, UserAccountState.password, chat_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(UserAccountCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        user_account=user_account_factory.filter())
