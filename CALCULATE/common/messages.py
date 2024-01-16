from telebot import TeleBot
from common.utils import float_to_print, get_decimal_count, get_lang, get_print_float

from db import db


BULLET = '✦'


# Основные страницы
def msg_main(user_id: int, uses_count: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Меню',
            '1': 'Выберите рынок',
            '2': 'Укажите цифры',
            '3': 'Получите точные расчеты',
            'uses': 'Бесплатных расчетов',
        },
        'en': {
            'name': 'Menu',
            '1': 'Choose the market',
            '2': 'Indicate the numbers',
            '3': 'Get accurate calculations',
            'uses': 'Free calculations',
        }
    }

    return '\n'.join((
        f'⚡️ <b><u>{texts[lang]["name"]}</u></b>',
        '',
        f'1. <b>{texts[lang]["1"]}</b>',
        f'2. <b>{texts[lang]["2"]}</b>',
        f'3. <b>{texts[lang]["3"]}</b>',
        '',
        f'{texts[lang]["uses"]}: <b>{uses_count}</b>'
    ))


def msg_no_uses(user_id: int):
    lang = get_lang(user_id)
    text = {
        'ru': {
            '1': 'Тестовые 100 использований закончились',
            '2': 'Перейдите в бота сигналов для покупки доступа'
        },
        'en': {
            '1': 'Test 100 uses are over',
            '2': 'Go to the signal bot for buying access'
        },
    }
    return '\n'.join((
        f'❗️ {text[lang]["1"]}',
        f'{text[lang]["2"]}',
    ))


def msg_settings(user_id: int):
    lang = get_lang(user_id)
    base = db.get_user_base(user_id)
    tp_show: str = db.get_calculator_tp_show(user_id) or '345'

    texts = {
        'ru': {
            'name': 'Настройки',
            'dep': 'Базовый депозит',
            'risk': 'Базовый процент риска',
            'currency': 'Базовая валюта',
            'tp_show': 'Вывод расчета прибыли'
        },
        'en': {
            'name': 'Settings',
            'dep': 'Default deposit',
            'risk': 'Default risk percent',
            'currency': 'Default currency',
            'tp_show': 'Display calculation of profit'
        },
    }

    result = ''
    for el in tp_show:
        result += f'x{el} '

    return '\n'.join((
        f'⚙️ <b><u>{texts[lang]["name"]}</u></b>',
        '',
        f'{BULLET} {texts[lang]["dep"]}: <b>{float_to_print(base["base_deposit"])}</b>',
        f'{BULLET} {texts[lang]["risk"]}: <b>{float_to_print(base["base_risk_percent"])}</b>',
        f'{BULLET} {texts[lang]["currency"]}: <b>{base["base_currency"] or "-"}</b>',
        '',
        f'{BULLET} {texts[lang]["tp_show"]}: <b>{result}</b>'
    ))


def msg_settings_change_base(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Изменение значений',
        },
        'en': {
            'name': 'Settings',
            'subname': 'Change base',
        },
    }

    return f'⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>'


def msg_settings_set_tp_show(user_id: int):
    lang = get_lang(user_id)
    tp_show: str = db.get_calculator_tp_show(user_id) or '345'

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Установка расчета прибыли',
            'now': 'Сейчас выводится'
        },
        'en': {
            'name': 'Settings',
            'subname': 'Set calculation of profit',
            'now': 'Now displayed'
        }
    }

    result = ''
    for el in tp_show:
        result += f'x{el} '

    return '\n'.join((
        f'⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>',
        '',
        f'{texts[lang]["now"]}: <b>{result}</b>'
    ))


def msg_support(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Чтобы связаться с оператором тех.поддержки, нажмите на кнопку ниже',
        'en': 'To contact the technical support operator, click on the button below'
    }

    return f'{texts[lang]}👇'


# Первые сообщения
def msg_welcome(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            '1': 'Приветствую, трейдер',
            '2': 'Добро пожаловать в мир точных расчетов и успешных сделок! Здесь ты найдешь своего верного компаньона – Калькулятор трейдинга. 📈✨ Готов покорять финансовые вершины?',
            '3': 'Введем твои базовые данные? 🌐📊'
        },
        'en': {
            '1': 'Greetings, trader',
            '2': 'Welcome to the realm of precise calculations and successful trades! Here, you\'ll discover your reliable companion – the Trading Calculator. 📈✨ Ready to conquer financial peaks?',
            '3': 'Let\'s enter your basic data?🌐📊'
        }
    }

    return '\n'.join((
        f'⚡️ {texts[lang]["1"]}! 🚀',
        f'{texts[lang]["2"]}',
        '',
        f'{texts[lang]["3"]}',
    ))


def msg_success_base_set(user_id):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            '1': 'Базовые значения сохранены',
            '2': 'Поменять их можно в настройках'
        },
        'en': {
            '1': 'The basic values are saved',
            '2': 'You can change them in the settings'
        },
    }

    return '\n'.join((
        f'✅ {texts[lang]["1"]}!',
        f'{texts[lang]["2"]} ⚙️'
    ))


# Базовые
def msg_success_edit(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Изменения сохранены',
        'en': 'Changes saved'
    }

    return f'✅ {texts[lang]}!'


# Ошибки ввода данных
def msg_ticker_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите тикер текстом',
        'en': 'Enter the ticker in text'
    }

    return f'❗️ {texts[lang]}:'


def msg_ticker_not_found(user_id: int, ticker: str):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            '1': 'В нашей базе нет фьючерса с кодом',
            '2': 'Введите тикер фьючерса (буквенный, пример: siz2)'
        },
        'en': {
            '1': 'There is no futures with a code in our database',
            '2': 'Enter the futures ticker (example: siz2)'
        }
    }

    return '\n'.join([
        f'❗️ {texts[lang]["1"]} {ticker}',
        f'{texts[lang]["2"]}:'
    ])


def msg_paire_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите валютную пару текстом',
        'en': 'Enter the currency pair by text'
    }

    return f'❗️ {texts[lang]}:'


def msg_paire_not_found(user_id: int, paire: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'В базе нет пары',
        'en': 'There is no pair in the base'
    }

    return f'❗️ {texts[lang]} {paire}:'


def msg_digit_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите число',
        'en': 'Enter a number'
    }

    return f'❗️ {texts[lang]}:'


def msg_percent_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите число (от 0 до 100)',
        'en': 'Enter a number (from 0 to 100):'
    }

    return f'❗️ {texts[lang]}:'


def msg_sl_op_equal_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Цена стоп лосса и входа равны',
        'en': 'The price of the stop loss and entry are equal'
    }

    return f'⚠️ {texts[lang]}:'


def msg_currency_error(user_id):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите валюту текстом',
        'en': 'Enter the currency with text'
    }

    return f'❗️ {texts[lang]}:'


# Калькулятор
def msg_calculate(bot: TeleBot, user_id: int, chat_id: int):
    lang = get_lang(user_id)
    currency = db.get_user_base(user_id)['base_currency'] or 'USD'

    with bot.retrieve_data(user_id, chat_id) as data:
        type = data.get('calc_type')
        ticker = data.get('ticker')
        deposit = data.get('deposit')
        risk_percent = data.get('risk_percent')
        open_price = data.get('open_price')

    name = {
        'ru': {
            'crypto': 'Криптовалюта',
            'paper': 'Акции',
            'future': 'Фьючерсы',
            'forex': 'Форекс'
        },
        'en': {
            'crypto': 'Cryptocurrency',
            'paper': 'Stocks',
            'future': 'Futures',
            'forex': 'Forex'
        }
    }

    type_list = ['ticker', 'dep', 'risk', 'open']
    vars_dict = {
        'ticker': ticker,
        'dep': deposit,
        'risk': risk_percent,
        'open': open_price,
    }
    point = {
        'ru': {
            'ticker': 'Тикер',
            'dep': 'Депозит',
            'risk': 'Процент риска',
            'open': 'Цена входа',
        },
        'en': {
            'ticker': 'Ticker',
            'dep': 'Deposit',
            'risk': 'Risk percent',
            'open': 'Entry price',
        }
    }

    text = f'💵 <b><u>{name[lang][type] or "Forex"}</u></b>\n'
    text += '\n'

    for el in type_list:
        item = vars_dict[el]
        if item is not None:
            if item == 'ticker':
                text += f'{BULLET} {point[lang][el]}: <b>{item}</b>\n'
            else:
                text += (
                    f'{BULLET} {point[lang][el]}: '
                    f'<b>{get_print_float(item, get_decimal_count(item))} {currency}</b>\n'
                )

    text += '\n'

    return text


def msg_calculate_result(
    user_id: int,
    deposit: float,
    risk_percent: float,
    open_price: float,
    stop_loss: float,
    take_profit_1: float,
    take_profit_2: float,
    take_profit_3: float,
    count_bet: float,
    summary_open_value: float,
    credit: int,
    risk_value: float,
):
    lang = get_lang(user_id)
    currency = db.get_user_base(user_id)['base_currency'] or 'USD'
    tp_show: str = db.get_calculator_tp_show(user_id) or '345'

    point = {
        'ru': {
            'dep': 'Депозит',
            'risk': '% риска на сделку',
            'open': 'Цена открытия',
            'sl': 'Стоп лосс',
            'tp': 'Тейк профит',
            'count': 'Приобретаем',
            'sum': 'Покупаем на',
            'credit': 'Кредитное плечо',
            'risk_val': 'Риск на сделку',
            'profit': 'Прибыль'
        },
        'en': {
            'dep': 'Deposit',
            'risk': '% risk of a deal',
            'open': 'The open price',
            'sl': 'Stop loss',
            'tp': 'Take profit',
            'count': 'Purchase',
            'sum': 'Buy on',
            'credit': 'Leverage',
            'risk_val': 'The risk of a deal',
            'profit': 'Profit'
        }
    }

    round_count = max(get_decimal_count(open_price),
                      get_decimal_count(stop_loss))

    return '\n'.join([
        f'{BULLET} {point[lang]["dep"]}: <b>{get_print_float(deposit)} {currency}</b>',
        f'{BULLET} {point[lang]["risk"]}: <b>{get_print_float(risk_percent)}%</b>',
        '',
        f'{BULLET} {point[lang]["open"]}: <b>{open_price} {currency}</b>',
        f'{BULLET} {point[lang]["sl"]}: <b>{stop_loss} {currency}</b>',
        ''.join((
            f'{BULLET} {point[lang]["tp"]}: <b>',
            f'{get_print_float(take_profit_1, round_count)} {currency}' if '3' in tp_show else '',
            ' / ' if ('3' in tp_show and ('4' in tp_show or '5' in tp_show)) else '',
            f'{get_print_float(take_profit_2, round_count)} {currency}' if '4' in tp_show else '',
            ' / ' if ('4' in tp_show and '5' in tp_show) else '',
            f'{get_print_float(take_profit_3, round_count)} {currency}' if '5' in tp_show else '',
            '</b>',
        )),
        f'{BULLET} {point[lang]["count"]}: <b>{get_print_float(count_bet)}</b> монет',
        '',
        f'{BULLET} {point[lang]["sum"]}: <b>{get_print_float(summary_open_value)} {currency}</b>',
        f'{BULLET} {point[lang]["credit"]}: <b>{int(credit)} к 1</b>',
        f'{BULLET} {point[lang]["risk_val"]}: <b>{get_print_float(risk_value)} {currency}</b>',

        ''.join((
            f'{BULLET} {point[lang]["profit"]}: <b> ',
            f'{get_print_float(risk_value * 3)} {currency}' if ("3" in tp_show) else "",
            ' / ' if ('3' in tp_show and ('4' in tp_show or '5' in tp_show)) else '',
            f'{get_print_float(risk_value * 4)} {currency}' if ("4" in tp_show) else "",
            ' / ' if ('4' in tp_show and '5' in tp_show) else '',
            f'{get_print_float(risk_value * 5)} {currency}' if ("5" in tp_show) else "",
            '</b>',
        ))
    ])


def msg_calculate_forex_result(
    user_id: int,
    deposit: float,
    val_dep: str,
    risk_percent: float,
    paire: str,
    open_price: float,
    stop_loss: float,
    take_profit_1: float,
    take_profit_2: float,
    take_profit_3: float,
    lot: float,
    risk_value: float,
):
    lang = get_lang(user_id)

    point = {
        'ru': {
            'dep': 'Депозит',
            'risk': '% риска на сделку',
            'paire': 'Валютная пара',
            'open': 'Цена открытия',
            'sl': 'Стоп лосс',
            'tp': 'Тейк профит',
            'lot': 'Лот',
            'risk_val': 'Риск на сделку',
            'profit': 'Прибыль'
        },
        'en': {
            'dep': 'Deposit',
            'risk': '% risk of a deal',
            'paire': 'Currency pair',
            'open': 'Цена открытия',
            'sl': 'Stop loss',
            'tp': 'Take profit',
            'lot': 'Lot',
            'risk_val': 'The risk of a deal',
            'profit': 'Profit'
        }
    }

    return '\n'.join([
        f'{BULLET} {point[lang]["dep"]}: <b>{deposit} {val_dep}</b>',
        f'{BULLET} {point[lang]["risk"]}: <b>{risk_percent}</b>',
        '',
        f'{BULLET} {point[lang]["paire"]}: <b>{paire}</b>',
        f'{BULLET} {point[lang]["open"]}: <b>{open_price}</b>',
        f'{BULLET} {point[lang]["sl"]}: <b>{stop_loss}</b>',
        f'{BULLET} {point[lang]["tp"]}: <b>{round(take_profit_1, 2)} / {round(take_profit_2, 2)} / {round(take_profit_3, 2)}</b>',
        f'{BULLET} {point[lang]["lot"]}: <b>{round(lot, 2)}</b>',
        '',
        f'{BULLET} {point[lang]["risk_val"]}: <b>{risk_value} {val_dep}</b>',
        f'{BULLET} {point[lang]["profit"]}: <b>{round(risk_value * 2, 2)} / {round(risk_value * 3, 2)} / {round(risk_value * 4, 2)}</b>'
    ])


# Ввод данных
def msg_enter_future(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите тикер фьючерса (буквенный, пример: siz2)',
        'en': 'Enter the futures ticker (example: siz2)'
    }

    return f'✍ {texts[lang]}:'


def msg_enter_deposit(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите размер депозита',
        'en': 'Enter the size of the deposit'
    }

    return f'✍ {texts[lang]}:'


def msg_enter_risk_percent(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите % риска на сделку',
        'en': 'Enter % risk of a deal'
    }

    return f'✍ {texts[lang]}:'


def msg_enter_currency(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите валюту',
        'en': 'Enter the currency'
    }

    return f'✍ {texts[lang]}:'


def msg_enter_paire(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите валютную пару',
        'en': 'Enter the currency pair'
    }

    return f'✍ {texts[lang]} (XXX XXX):'


def msg_enter_open_price(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите цену открытия сделки',
        'en': 'Enter the price of the opening transaction'
    }

    return f'✍ {texts[lang]}:'


def msg_enter_stop_loss(user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        text = 'Введите цену стоп лосса:'
    else:
        text = 'Enter the stop loss price'

    return f'✍ {text}'


def msg_choose_lang(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Выберите язык',
        'en': 'Choose language'
    }

    return f'🌐 {texts[lang]}'


# Инструкция к калькулятору
msg_manual = ["""
❗️ *Как работать с калькулятором:*

*1.* Выбираете рынок, которым торгуете

Каждый из них имеет свои формулы расчетов, потому будете *внимательны.*    
""",
              """
*2.* Вводите сумму депозита

Валюта может быть любая.
Это не имеет значения при подсчете.

Если считаете в рублях, то и объем укажет, исходя из этих данных.
""",
              """
*3.* Введите сумму риска.

Сумма депозита выбрана в 100 00 (пусть будет рублей)

Рекомендовано (особенно для внутридневной торговли) брать не более 1-2% на депозит

Если у Вас более 1 сделки внутри дня, то лучше разбить сумму риска на все сделки. 

*Дано:*
- депозит: 100 000 рублей
- риск в 1%: 1 000 рублей 

Если мы получаем стоп-лосс, то отдаем рынку не более 1 000 рублей 

Таким образом, математически у нас есть 100 попыток для увеличения капитала.
""",
              """
*4.* Вводите исходные данные для расчета объема

*а. Цена открытия. *

место, где находится Ваш уровень, откуда Вы готовы войти в сделку (либо на покупку (лонг), либо продажу (шорт)). 

Я выставил цифру (условную) в 50 

*б. Цена стоп-лосса:* 

цена, по которой продам свой объем рынку, если цена пойдет не в нашу сторону. 

Я указал цену в *49*

стоит цене в 1 пункт сходить не в мою сторону, как сделка будет закрыта автоматически. 

*в. Цена тейк-профита:*

цена, при которой мы успешно закроем сделку, когда он дойдет до нужного нам уровня цены 

Я указал *в 55*

Теперь, когда вводные данные есть, смотрим на результат:
""",
              """
*5. Результаты: *

Видим, как система показала нам все исходные введенные данные и высчитала объем для входа в сделку

*Объем: 1 000 штук *

Теперь, когда у Вас есть такой инструмент для подсчетов, Вы всегда знаете где входить, выходить и фиксировать свой профит, предварительно зная и количество приобретенных монет/фьючерсов/акций 

Приятного использования.
"""
              ]
