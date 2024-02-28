from telebot import TeleBot
from telebot.types import Message

from initialize import pay_guard

from models import Update, Invoice, UpdateBBanker, InvoiceBBanker

from db_new import db_new
from keyboard_reply import kb_user_sup

from CALCULATE.callbacks import send_manual_page
from CALCULATE.commands import _start as _calc
from MAIN.start import send_start_by_user


from NOTIFIER import notifier
from NOTIFIER.messages import mess_set_trial_subsctibe_new_user


def _start(message: Message, bot: TeleBot, data: dict):
    chat_id = message.chat.id
    user_id = message.from_user.id

    user_role: int = data.get('user_role') or 0
    has_registered_now: bool = data.get('has_registered_now') or False

    send_start_by_user(
        bot, message, user_id,
        user_role, has_registered_now,
    )


def _faq(message: Message, bot: TeleBot):
    text = db_new.get_text_by_name('FAQ')
    msg = text.message if (text is not None) else '*Ошибка*'

    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _about_us(message: Message, bot: TeleBot):
    text = db_new.get_text_by_name('О нас')
    msg = text.message if (text is not None) else '*Ошибка*'

    bot.send_message(message.chat.id, msg)
    bot.delete_state(message.from_user.id, message.chat.id)


def _support(message: Message, bot: TeleBot):
    sup = db_new.get_support_name()
    msg = 'Чтобы связаться с оператором тех.поддержки, нажмите на кнопку ниже👇'

    bot.send_message(message.chat.id, msg, reply_markup=kb_user_sup(sup))
    bot.delete_state(message.from_user.id, message.chat.id)


def _manual(message: Message, bot: TeleBot):
    send_manual_page(message, bot, 1, message.from_user.id, True)


# def _calc(message: Message, bot: TeleBot):
#     send_main(message, bot, message.from_user.id, True)


def _test_check_func(message: Message, bot: TeleBot):
    print(f'🎶 🎶 🎶 🎶 🎶 🎶 Проверяем код!!!! 🎶 🎶 🎶 🎶 🎶 🎶')

    return False
    # Дерагаем оплату - проверяем проводку и применение подписки пользователю
    # Update
    # pay_load = Invoice(
    #     invoice_id=1,
    #     status='',
    #     asset='',
    #     amount=0.01,
    #     pay_url= 'url',
    #     description='Описалово',
    #     allow_comments=False,
    #     allow_anonymous=False
    # )
    # update = Update(
    #     update_id=1,
    #     update_type='',
    #     request_date='',
    #     payload=pay_load,
    # )

    # Оплата через CryptoBot pay
    update = Update
    update.payload = Invoice
    update.payload.status = 'paid'
    # 6278837 # сигналы # amount = 21
    # 6278846 # калькулятор # amount = 30
    # 6278848 # калькулятор+сигналы # amount = 50
    update.payload.invoice_id = 6278848
    update.payload.amount = 0.05
    update.payload.asset = 'USDT'
    print(f'update Тестируем активацию подписки по апдейту')
    print(update)
    # invoice_paid(update)

    # pays.get_updates_check(update) # invoice_paid_prev

    return False

    # Оплата через BitBanker
    update = UpdateBBanker()
    payload = InvoiceBBanker()

    # 2lwKEFfwP396OzHVgviLlB # калькулятор+сигналы # amount = 50
    payload.status = 'paid'
    payload.invoice_id = '2lwKEFfwP396OzHVgviLlB'
    payload.amount = 50
    payload.asset = 'USDT'
    update.payload = payload



    # pays_banker.get_updates_check(update) # invoice_paid




    return False
    # user_id = 777
    # print(f'Удаляем пользователя - с id{user_id} ')

    return False
    new_user = db_new.get_user_by_tg_id(message.from_user.id)
    notifier.send_notification('text', mess_set_trial_subsctibe_new_user(
        user_id=new_user.id,
        user_nike='@' + new_user.username if new_user.username else new_user.tg_id,
        days=pay_guard.get_option_trial_days()
    ))

    return False
    users = pay_guard.get_valid_users_for_signals()
    print(f'users ')
    print(users)
    return False

    # tariff_manager.switch_off_finish_tariffs()
    tariff = db_new.get_first_tariff_by_product()
    print(f'tariff ')
    print(tariff)
    print(
        f'tariff.name [{tariff.name}] tariff.id [{tariff.id}] tariff.type_product [{tariff.type_product}]')
    return False


def commands_registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(_start, commands=['start'])
    reg_mes(_start, commands=['signals'])

    reg_mes(_faq, commands=['faq'])
    reg_mes(_about_us, commands=['about_us'])

    reg_mes(_support, commands=['support'])
    reg_mes(_support, commands=['team'])

    reg_mes(_manual, commands=['manual'])
    reg_mes(_calc, commands=['calc'])

    reg_mes(_test_check_func, commands=['tasty'])
