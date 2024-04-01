from telebot import TeleBot
from datetime import datetime
from common.dt import get_str_by_datetime

from common.utils import get_lang, get_print_float
from db import LANGUAGES_TYPE, db
from models import Calculation


POINT = '•'
TAB = '   '

market_translates = {
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


def get_risk_annotation(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            '1': '<i>Cо знаком %</i> - для ввода процента риска от депозита',
            '2': '<i>Без знаков</i> - для ввода точной суммы риска',
        },
        'en': {
            '1': '<i>With a sign of %</i> - for entering a percentage of risk from a deposit',
            '2': '<i>Without signs</i> - for entering a cloth amount of risk',
        }
    }

    return f"""{texts[lang]['1']}
{texts[lang]['2']}
"""


# Основные страницы
def msg_uses_count(user_id: int, count: int):
    lang = get_lang(user_id)

    text = {
        'ru': {
            'uses': 'Бесплатных расчетов',
        },
        'en': {
            'uses': 'Free calculations',
        }
    }

    return f'{text[lang]["uses"]}: <b>{count}</b>'


def msg_main(user_id: int, uses_count: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Меню',
            '1': 'Настройте калькулятор',
            '2': 'Получите точные расчеты',
            'uses': 'Бесплатных расчетов',
        },
        'en': {
            'name': 'Menu',
            '1': 'Choose the market',
            '2': 'Get accurate calculations',
            'uses': 'Free calculations',
        }
    }

    return f"""
⚡️ <b><u>{texts[lang]["name"]}</u></b>

1. <b>{texts[lang]["1"]}</b>
2. <b>{texts[lang]["2"]}</b>

{msg_uses_count(user_id, uses_count)}
"""


def msg_no_uses(user_id: int):
    lang = get_lang(user_id)
    text = {
        'ru': {
            '1': 'Тестовые 100 использований закончились',
            '2': 'Перейдите в бота рекомендаций для покупки доступа'
        },
        'en': {
            '1': 'Test 100 uses are over',
            '2': 'Go to the signal bot for buying access'
        },
    }

    return f"""
❗️ {text[lang]["1"]}
{text[lang]["2"]}
"""


def msg_main_freeze(user_id: int, freeze_dt: datetime):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Меню',
        },
        'en': {
            'name': 'Menu',
        }
    }

    return f"""
⚡️ <b><u>{texts[lang]["name"]}</u></b>

❄️ Калькулятор заморожен до <b>{get_str_by_datetime(freeze_dt)}</b>
"""


def msg_settings(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)

    u_base = db.get_calc_user_settings(user_db_id)
    if u_base is None:
        return ''

    texts = {
        'ru': {
            'name': 'Настройки',
            'dep': 'Базовый депозит',
            'risk': 'Базовый риск',
            'day_risk': 'Риск на день',
            'round_count': 'Округление до',
            'trading_style': 'Стиль торговли',
            'currency': 'Базовая валюта',
            'tp_show': 'Деление профита',
            'market': 'Рынок',
            'round_count': 'Округление',
        },
        'en': {
            'name': 'Settings',
            'dep': 'Default deposit',
            'risk': 'Default risk',
            'day_risk': 'Daily risk',
            'round_count': 'Rounding',
            'trading_style': 'Trading style',
            'currency': 'Default currency',
            'tp_show': 'Profit division',
            'market': 'Market',
        },
    }

    currency = u_base.currency or 'USD'

    tp_result = ''
    for el in u_base.tp_ratio:
        tp_result += f'x{el} '

    show_deposit = f"{get_print_float(u_base.deposit)} {currency}" if (
        u_base.deposit is not None) else "-"

    show_risk = (str(get_print_float(u_base.risk[0])) +
                 ("%" if u_base.risk[1] else f" {currency}")) if (u_base.risk is not None) else "-"

    show_day_risk = (f'{get_print_float(u_base.day_risk[0])}' +
                     ('%' if u_base.day_risk[1] else f' {currency}')) if (u_base.day_risk is not None) else "-"

    return f"""
⚙️ <b><u>{texts[lang]["name"]}</u></b>

{POINT} {texts[lang]["dep"]}: <b>{show_deposit}</b>
{POINT} {texts[lang]["risk"]}: <b>{show_risk}</b>
{POINT} {texts[lang]["trading_style"]}: <b>{u_base.trading_style or '-'}</b>

{POINT} {texts[lang]["day_risk"]}: <b>{show_day_risk}</b>
{POINT} {texts[lang]["round_count"]}: <b>{u_base.round_count or '-'}</b>

{POINT} {texts[lang]["tp_show"]}: <b>{tp_result}</b>
{POINT} {texts[lang]["market"]}: <b>{market_translates[lang][u_base.market]}</b>
"""


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


def msg_settings_change_market(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Изменение рынка',
        },
        'en': {
            'name': 'Settings',
            'subname': 'Change market',
        },
    }

    return f'⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>'


def msg_summury_profit_settings(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)
    tp_ratio = u_base.tp_ratio if (u_base is not None) else []
    split_values = u_base.split_values if (u_base is not None) else None

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Деление профита',
            'take_profit': 'Ваш тейк-профит',
            'split': 'Разделение',
            'on': 'включено',
            'off': 'выключено',
        },
        'en': {
            'name': 'Settings',
            'subname': 'Profit division',
            'take_profit': 'Your take profit',
            'split': 'Splitting',
            'on': 'turned on',
            'off': 'turned off',
        }
    }

    info_result = ''

    if split_values is not None:
        on_off = "on"

        for i, el in enumerate(tp_ratio):
            info_result += f'<b>x{el} ({split_values[i]}%)</b>'

            if i == len(tp_ratio) - 1:
                pass
            elif i % 3 != 2:
                info_result += ' - '
            else:
                info_result += '\n'
    else:
        on_off = "off"

        info_result = f'{texts[lang]["take_profit"]}: '
        for i, el in enumerate(tp_ratio):
            info_result += f'<b>x{el}</b>'
            if i != len(tp_ratio) - 1:
                info_result += ' - '

    return f"""
⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>

{texts[lang]["split"]}: <b>{texts[lang][on_off]}</b>
{info_result}
"""


def msg_support(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Чтобы связаться с оператором тех.поддержки, нажмите на кнопку ниже',
        'en': 'To contact the technical support operator, click on the button below'
    }

    return f'{texts[lang]}👇'


def msg_stats(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    all_stats = db.get_calculations_by_user(user_db_id)
    saved_stats = db.get_calculations_by_user(user_db_id, True)

    user_settings = db.get_calc_user_settings(user_db_id)

    currency = 'USD'
    if user_settings is not None:
        currency = user_settings.currency or currency

    tp_count = 0
    sl_count = 0

    profit = 0
    for stat in saved_stats:
        stat_profit = stat.profit or 0

        if stat_profit > 0:
            tp_count += 1
        if stat_profit < 0:
            sl_count += 1

        profit += stat_profit

    texts = {
        'ru': {},
        'en': {}
    }

    return f"""📊 <u><b>Статистика</b></u>

{POINT} Всего расчетов: <b>{len(all_stats)} шт.</b>

{POINT} Тейк-профит: <b>{tp_count} шт.</b>
{POINT} Стоп-лосс: <b>{sl_count} шт.</b>
{POINT} Общее: <b>{len(saved_stats)} шт.</b>

{POINT} Сумма: <b>{get_print_float(profit)} {currency}</b>
"""


def msg_freeze_calc(user_id: int, risk_value: float, currency='', is_percent=False):
    if is_percent:
        risk_show = f'<b>{get_print_float(risk_value)}%</b> от депозита'
    else:
        risk_show = f'<b>{get_print_float(risk_value)} {currency}</b>'

    return f"""⚠️ Вы превысили суточный процент риска на {risk_show}.
<b>Желаете приостановить торговлю на некоторое время?</b>

✍️ Введите <i>время</i> заморозки в формате <u>ЧЧ:ММ</u>.
✍️ Либо <i>дату до</i> в формате <u>ДД.ММ.ГГГГ ЧЧ:ММ</u>.

На это время расчеты в калькуляторе невозможно будет совершать для безопасности Вашей торговли.
"""


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

    return f"""
⚡️ {texts[lang]["1"]}! 🚀
{texts[lang]["2"]}

{texts[lang]["3"]}
"""


def msg_success_base_set(user_id: int):
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

    return f"""
✅ {texts[lang]["1"]}!
{texts[lang]["2"]} ⚙️
"""


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

    return f"""
❗️ {texts[lang]["1"]} {ticker}
{texts[lang]["2"]}:
"""


def msg_pair_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите валютную пару текстом',
        'en': 'Enter the currency pair by text'
    }

    return f'❗️ {texts[lang]}:'


def msg_pair_not_found(user_id: int, pair: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'В базе нет пары',
        'en': 'There is no pair in the base'
    }

    return f'❗️ {texts[lang]} {pair}:'


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

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)
    if u_base is None:
        return ''

    deposit = u_base.deposit
    risk = u_base.risk
    currency = u_base.currency or 'USD'

    risk_value = risk[0] if (risk is not None) else None
    if (risk is not None) and risk[1] and (deposit is not None):
        risk_value = risk[0] * deposit * 0.01

    with bot.retrieve_data(user_id, chat_id) as data:
        type = data.get('calc_type')
        ticker = data.get('ticker')
        open_price = data.get('open_price')

    type_list = ['ticker', 'dep', 'risk', 'open']
    vars_dict = {
        'ticker': ticker,
        'dep': deposit,
        'risk': risk_value,
        'open': open_price,
    }

    point = {
        'ru': {
            'ticker': 'Тикер',
            'dep': 'Депозит',
            'risk': 'Риск на сделку',
            'open': 'Цена входа',
        },
        'en': {
            'ticker': 'Ticker',
            'dep': 'Deposit',
            'risk': 'Deal risk',
            'open': 'Entry price',
        }
    }

    text = f'💵 <b><u>{market_translates[lang][type] or "Forex"}</u></b>\n'
    text += '\n'

    for el in type_list:
        item = vars_dict[el]
        if item is not None:
            if item == 'ticker':
                text += f'{POINT} {point[lang][el]}: <b>{item}</b>\n'
            else:
                text += (
                    f'{POINT} {point[lang][el]}: '
                    f'<b>{get_print_float(item, 4)} {currency}</b>\n'
                )

    text += '\n'

    return text


def msg_calculate_result(
    user_id: int,
    calc: Calculation,
):
    if calc.forex_info is not None:
        return msg_calculate_forex_result(user_id, calc)
    else:
        return msg_calculate_crypto_result(user_id, calc)


def msg_calculate_crypto_result(
    user_id: int,
    calc: Calculation,
):
    lang = get_lang(user_id)

    point = {
        'ru': {
            'dep': 'Депозит',
            'open': 'Цена входа',
            'sl': 'Стоп лосс',
            'conclusion': 'Тейк-профит',
            'split': 'Разделение',
            'count': 'Приобретаем',
            'sum': 'Покупаем на',
            'style': 'Стиль торговли',
            'risk_val': 'Риск на сделку',
            'profit': 'Прибыль по сделке'
        },
        'en': {
            'dep': 'Deposit',
            'open': 'Open price',
            'sl': 'Stop loss',
            'conclusion': 'Take-profit',
            'split': 'Split',
            'count': 'Purchase',
            'sum': 'Buy on',
            'style': 'Trading style',
            'risk_val': 'The risk of a deal',
            'profit': 'Profit'
        }
    }

    # Округление
    round_count = calc.round_count or 5

    # Кол-во покупки
    count_bet = (
        calc.risk_value /
        max(abs(calc.open_price - calc.stop_loss), 0.01)
    )  # * rate

    # Сумма покупки
    value_bet = count_bet * calc.open_price

    p_show = ''
    conclusion = ''
    for i in range(len(calc.tp_ratio)):
        rate = 1
        tp_ratio_i = calc.tp_ratio[i]
        tp_i = get_print_float(
            max(calc.open_price + (calc.open_price - calc.stop_loss) * tp_ratio_i, 0),
            round_count
        )

        conclusion += f'  <b>x{tp_ratio_i}</b>: <u>{tp_i} {calc.currency}</u>'

        if calc.split_values is not None and len(calc.split_values) != 0:
            percent = calc.split_values[i]
            rate = percent / 100

            count = get_print_float(count_bet * rate, 2)

            conclusion += f' (<b>{count} монет</b>) — {get_print_float(percent, round_count)}%'

        p_show += f'{get_print_float(abs(calc.open_price - tp_i) * rate * count_bet, round_count)}'

        if i != len(calc.tp_ratio) - 1:
            conclusion += '\n'
            p_show += ' / '

    return f"""{POINT} {point[lang]["dep"]}: <b>{get_print_float(calc.deposit)} {calc.currency}</b>
{TAB}{point[lang]["risk_val"]}: <b>{get_print_float(calc.risk_value)} {calc.currency}</b>

{POINT} {point[lang]["open"]}: <b>{get_print_float(calc.open_price, round_count)} {calc.currency}</b>
{TAB}{point[lang]["sl"]}: <b>{get_print_float(calc.stop_loss, round_count)} {calc.currency}</b>

{POINT} {point[lang]["count"]}: <b>{get_print_float(count_bet)} монет</b>
{TAB}{point[lang]["sum"]}: <b>{get_print_float(value_bet)} {calc.currency}</b>
{TAB}{point[lang]["style"]}: <b>{calc.trading_style.capitalize()}</b>

{POINT} {point[lang]['conclusion']}:
{conclusion}

{POINT} {point[lang]["profit"]}: <b>{p_show}</b>
"""


def msg_calculate_forex_result(
    user_id: int,
    calc: Calculation,
):
    if calc.forex_info is None:
        return 'Ошибка'

    pair = '/'.join(calc.forex_info.pair)
    LOT = pow(10, 5)

    lang = get_lang(user_id)

    point = {
        'ru': {
            'pair': 'Валютная пара',
            'dep': 'Депозит',
            'open': 'Цена входа',
            'sl': 'Стоп лосс',
            'tp': 'Тейк профит',
            'conclusion': 'Тейк-профит',
            'split': 'Разделение',
            'count': 'Приобретаем',
            'sum': 'Покупаем на',
            'style': 'Стиль торговли',
            'risk_val': 'Риск на сделку',
            'profit': 'Прибыль по сделке'
        },
        'en': {
            'pair': 'Currency pair',
            'dep': 'Deposit',
            'open': 'Open price',
            'sl': 'Stop loss',
            'tp': 'Take profit',
            'conclusion': 'Take-profit',
            'split': 'Split',
            'count': 'Purchase',
            'sum': 'Buy on',
            'style': 'Trading style',
            'risk_val': 'The risk of a deal',
            'profit': 'Profit'
        }
    }

    # Валюта торговли
    trading_currency = calc.forex_info.pair[1]

    # Округление
    round_count = calc.round_count or 5
    # Окургление pips
    round_pips = 2 if 'JPY' in pair else 4

    # Сумма покупки
    value_bet = (
        calc.risk_value /
        (max(abs(calc.open_price - calc.stop_loss), 0.000001))
    )
    # Кол-во покупки
    count_bet = value_bet / LOT

    if calc.currency == calc.forex_info.pair[1]:
        value_bet *= calc.open_price
    elif calc.currency == calc.forex_info.pair[0]:
        count_bet *= calc.stop_loss
        value_bet = count_bet * LOT
    else:
        BASExxx = f'{calc.currency}/{calc.forex_info.pair[1]}'
        yyyBASE = f'{calc.forex_info.pair[0]}/{calc.currency}'
        count_bet *= calc.forex_info.cross_prices.get(BASExxx, 1)
        value_bet = count_bet * LOT * \
            calc.forex_info.cross_prices.get(yyyBASE, 1)

    p_show = ''
    conclusion = ''
    for i in range(len(calc.tp_ratio)):
        rate = 1
        tp_ratio_i = calc.tp_ratio[i]
        tp_i = get_print_float(
            max(calc.open_price + (calc.open_price - calc.stop_loss) * tp_ratio_i, 0),
            round_count
        )

        conclusion += f'  <b>x{tp_ratio_i}</b>: <u>{tp_i} {trading_currency}</u>'

        if calc.split_values is not None and len(calc.split_values) != 0:
            percent = calc.split_values[i]
            rate = percent / 100

            count = get_print_float(count_bet * rate, 2)

            conclusion += f' (<b>{count} лота</b>) — {get_print_float(percent, round_count)}%'

        profit = abs(calc.open_price - tp_i) * rate * count_bet * pow(10, 5)
        if calc.forex_info.pair[0] == calc.currency:
            profit /= calc.stop_loss
        elif calc.forex_info.pair[1] != calc.currency:
            profit /= calc.forex_info.cross_prices.get(
                f'{calc.currency}/{calc.forex_info.pair[1]}', 1
            )

        p_show += f'{get_print_float(profit, round_count)}'

        if i != len(calc.tp_ratio) - 1:
            conclusion += '\n'
            p_show += ' / '

    return f"""
{POINT} {point[lang]["pair"]}: <b>{pair}</b>

{POINT} {point[lang]["dep"]}: <b>{get_print_float(calc.deposit)} {calc.currency}</b>
{TAB}{point[lang]["risk_val"]}: <b>{get_print_float(calc.risk_value)} {calc.currency}</b>

{POINT} {point[lang]["open"]}: <b>{get_print_float(calc.open_price, round_count)} {calc.forex_info.pair[1]}</b>
{TAB}{point[lang]["sl"]}: <b>{get_print_float(calc.stop_loss, round_count)} {calc.forex_info.pair[1]}</b>

{POINT} {point[lang]["count"]}: <b>{get_print_float(count_bet)} лота</b>
{TAB}{point[lang]["sum"]}: <b>{get_print_float(value_bet)} {calc.currency}</b>
{TAB}{point[lang]["style"]}: <b>{calc.trading_style.capitalize()}</b>

{POINT} {point[lang]['conclusion']}:
{conclusion}

{POINT} {point[lang]["profit"]} (<b>{calc.currency}</b>):
  <b>{p_show}</b>
"""


# Ввод данных
def msg_enter_take_profit(user_id: int, tp_ratio: list[int]):
    current_tp = tp_ratio.copy()
    current_tp.sort()

    tp_count = len(current_tp)

    text = '<u>Установка тейк-профита</u>\n'

    if tp_count != 0:
        text += 'Текущий выбор: <b>'

        for el in current_tp:
            text += f'x{el} '

        text += '</b>\n'

    text += '\nУчитывайте, что максимальный коэффициент тейк-профита - <b>x10</b>\n'
    text += 'Можно выбрать до <b>5</b> значений\n\n'

    if tp_count == 0:
        text += 'Выберите <b>первое</b> значение'
    elif tp_count == 5:
        text += 'Выберите действие'
    else:
        text += 'Выберите <b>следующее</b> значение'

    return text


def msg_enter_splitting(user_id: int, tp_ratio: list[int], split: list[float], is_last=False):
    tp_count = len(tp_ratio)
    split_count = len(split)

    if tp_count == 0 or split_count == 0:
        sorted_tp, sorted_split = [], []
    else:
        sorted_tp, sorted_split = zip(*sorted(zip(tp_ratio, split)))

    percents_sum = sum(split)
    if abs(percents_sum - 100) < 0.2:
        percents_sum = 100

    text = '<u>Установка разделения профита</u>\n'

    if tp_count != 0 and split_count != 0:
        text += '\n<u>Текущий выбор</u>: <b>\n'

        for i, el in enumerate(sorted_tp):
            try:
                percent = f'({get_print_float(sorted_split[i])}%)'
            except:
                percent = ''

            text += f'x{el} {percent}'

            if i == len(sorted_tp) - 1:
                pass
            elif i % 3 == 2:
                text += '\n'
            else:
                text += ' - '

        text += '</b>\n'
        text += f'<i>Суммарный процент:</i> <b>{get_print_float(percents_sum)}</b>\n'

    text += '\n'
    if is_last:
        text += f'Оставшиеся <b>{get_print_float(100-percents_sum, 2)}%</b> торговой позиции можно разбить. '
        text += 'Разбиение расчитает каждую из <i>n</i> частей для слудующих +1 тейк-профитов\n'
        text += 'Выберите на <u>сколько частей</u> разделить остаток'
    elif tp_count == 0:
        text += 'Выберите <b>первое</b> значение тейк-профита'
    elif tp_count == 5 or percents_sum == 100:
        text += 'Выберите действие'
    elif tp_count != split_count:
        text += f'Введите <b>процент вывода</b> для тейк-профита <b>x{tp_ratio[-1]}</b>'
    else:
        text += 'Выберите <b>следующее</b> значение тейк-профита'

    return text


def msg_enter_summury_profit_type(user_id: int):
    return """
Выберите вид разделения суммы:

<i>*Простой - без деления профита, продажа 100% торговой позиции
*Разделение - продажа торговой позиции разделяется на несколько тейк-профитов</i>
"""


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
        'ru': 'Введите <u>риск</u> на сделку',
        'en': 'Enter <u>risk</u> to the deal',
    }

    return f"""✍ {texts[lang]}

{get_risk_annotation(lang)}
"""


def msg_enter_day_risk(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите <u>риск на день</u>',
        'en': 'Enter <u>daily risk</u>',
    }

    return f"""✍ {texts[lang]}

{get_risk_annotation(lang)}
"""


def msg_enter_trading_style(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'choose': 'Выберите <u>стиль торговли</u> из списка ниже',
            'enter': 'Либо введите <i>свой вариант</i>'
        },
        'en': {
            'choose': 'Select <u>trading style</u> from the list below',
            'enter': 'Or enter <i>your option</i>'
        },
    }

    return f"""✍ {texts[lang]['choose']}
{texts[lang]['enter']}:
"""


def msg_enter_round_count(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Введите <u>количество знаков</u> после запятой',
            'max': '<i>Максимум</i>: <b>5</b>'
        },
        'en': {
            'main': 'Enter the <u>number of signs</u> after dot',
            'max': '<i>Maximum</i>: <b>5</b>'
        },
    }

    return f"""✍ {texts[lang]['main']}
{texts[lang]['max']}
"""


def msg_enter_currency(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите валюту или выберите из списка',
        'en': 'Enter the currency or select from the list'
    }

    return f'✍ {texts[lang]}:'


def msg_enter_pair(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите валютную пару',
        'en': 'Enter the currency pair'
    }

    return f"""✍ {texts[lang]} (XXX XXX):"""


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


def msg_enter_profit_minus(user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        text = 'Введите убыток по этой сделке:'
    else:
        text = 'Enter a loss of this transaction:'

    return f'✍ {text}'


def msg_choose_lang(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Выберите язык',
        'en': 'Choose language'
    }

    return f'🌐 {texts[lang]}'


def msg_confirm_reset(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Вы действительно хотите <b>сбросить</b> все настройки',
        'en': 'Do you really want to drop </b> all settings?',
    }

    return f'⚠️ {texts[lang]}?'


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

*а. Цена входа. *

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
