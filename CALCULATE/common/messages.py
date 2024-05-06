from typing import Literal
from telebot import TeleBot
from datetime import datetime

from common.calculation import get_count_value_bet
from common.dt import get_str_by_datetime
from common.utils import get_decimal_count, get_lang, get_print_float
from db import LANGUAGES_TYPE, db
from models import MARKETS_TYPE, Calculation, CalculatorStats, ForexInfo


POINT = '•'
TAB = '   '


market_translates: dict[LANGUAGES_TYPE, dict[MARKETS_TYPE, str]] = {
    'ru': {
        'crypto': 'Криптовалюта',
        'paper': 'Акции',
        'forex': 'Форекс',
        'RF': 'РФ',
        'USA': 'США',
    },
    'en': {
        'crypto': 'Cryptocurrency',
        'paper': 'Stocks',
        'forex': 'Forex',
        'RF': 'RF',
        'USA': 'USA',
    }
}


def get_risk_annotation(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            '1': '<i>Cо знаком %</i> - для ввода процента от депозита',
            '2': '<i>Без знаков</i> - для ввода точной суммы',
        },
        'en': {
            '1': '<i>With a sign of %</i> - for entering a percentage from a deposit',
            '2': '<i>Without signs</i> - for entering a cloth amount',
        }
    }

    return f"""{texts[lang]['1']}
{texts[lang]['2']}
"""


def get_freeze_annotation(lang: LANGUAGES_TYPE):
    texts = {
        'ru': {
            'time': 'Введите <i>время</i> заморозки в формате <u>ЧЧ:ММ</u>',
            'datetime': 'Либо <i>дату до</i> в формате <u>ДД.ММ.ГГГГ ЧЧ:ММ</u>',
        },
        'en': {
            'time': 'Enter <i>time</i> frost in format <u>HH:MM</u>',
            'datetime': 'Or <i>date to</i> in format <u>ДД.ММ.ГГГГ ЧЧ:ММ</u>',
        }
    }

    return f"""✍️ {texts[lang]['time']}.
✍️ {texts[lang]['datetime']}.
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

    return f"""⚡️ <b><u>{texts[lang]["name"]}</u></b>

{msg_frozen(user_id, get_str_by_datetime(freeze_dt))}
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
            'trading_type': 'Тип торговли',
            'updating_deposit': 'Обновление депозита',
            'currency': 'Базовая валюта',
            'tp_show': 'Деление профита',
            'market': 'Рынок',
            'round_count': 'Округление',
            'on': 'Включено',
            'off': 'Выключено',

            'margin': 'маржинальный',
            'spot': 'спотовый',
        },
        'en': {
            'name': 'Settings',
            'dep': 'Default deposit',
            'risk': 'Default risk',
            'day_risk': 'Daily risk',
            'round_count': 'Rounding',
            'trading_style': 'Trading style',
            'trading_type': 'Trading type',
            'updating_deposit': 'Deposit updating',
            'currency': 'Default currency',
            'tp_show': 'Profit division',
            'market': 'Market',
            'on': 'On',
            'off': 'Off',

            'margin': 'margin',
            'spot': 'spot',
        },
    }

    currency = u_base.currency or ''

    tp_result = ''
    for el in u_base.tp_ratio:
        tp_result += f'x{el} '

    show_deposit = '-'
    if u_base.deposit is not None:
        show_deposit = get_print_float(u_base.deposit)

    show_risk = (str(get_print_float(u_base.risk[0])) +
                 ("%" if u_base.risk[1] else f" {currency}")) if (u_base.risk is not None) else "-"

    show_day_risk = (f'{get_print_float(u_base.day_risk[0])}' +
                     ('%' if u_base.day_risk[1] else f' {currency}')) if (u_base.day_risk is not None) else "-"

    updating_deposit = texts[lang]['off']
    if u_base.is_updating_deposit:
        updating_deposit = texts[lang]['on']

    return f"""
⚙️ <b><u>{texts[lang]["name"]}</u></b>

{POINT} {texts[lang]["market"]}: <b>{market_translates[lang][u_base.market]}</b>

{POINT} {texts[lang]["dep"]}: <b>{show_deposit} {currency}</b>
{POINT} {texts[lang]["risk"]}: <b>{show_risk}</b>
{POINT} {texts[lang]["updating_deposit"]}: <b>{updating_deposit}</b>

{POINT} {texts[lang]["trading_style"]}: <b>{u_base.trading_style or '-'}</b>
{POINT} {texts[lang]["trading_type"]}: <b>{texts[lang][u_base.trading_type]}</b>
{POINT} {texts[lang]["tp_show"]}: <b>{tp_result}</b>

{POINT} {texts[lang]["day_risk"]}: <b>{show_day_risk}</b>
{POINT} {texts[lang]["round_count"]}: <b>{u_base.round_count or '-'}</b>"""


def msg_deposit(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    u_base = db.get_calc_user_settings(user_db_id)

    is_update = False
    deposit = '-'
    currency = 'USD'
    if u_base is not None:
        deposit = get_print_float(u_base.deposit or 0.) or deposit
        currency = u_base.currency or currency
        is_update = u_base.is_updating_deposit

    texts = {
        'ru': {
            'main': 'Настройка депозита',
            'dep': 'Текущий депозит',
            'update': 'Обновление после сохранения расчета',
            'on': 'включено',
            'off': 'выключено',
        },
        'en': {
            'main': 'Setup deposit',
            'dep': 'Current deposit',
            'update': 'Update after saving calculation',
            'on': 'on',
            'off': 'off',
        },
    }

    return f"""<b><u>{texts[lang]['main']}</u></b>

{POINT} {texts[lang]['dep']}: <b>{deposit} {currency}</b>
{POINT} {texts[lang]['update']}: <b>{texts[lang]['on'] if is_update else texts[lang]['off']}</b>
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
        'ru': 'Чтобы связаться с оператором тех. поддержки, нажмите на кнопку ниже',
        'en': 'To contact the technical support operator, click on the button below'
    }

    return f'{texts[lang]}👇'


def msg_stats_page(user_id: int, count: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Статистика',
            'count': 'Всего расчетов',
        },
        'en': {
            'main': 'Stats',
            'count': 'Calculations count',
        },
    }

    return f"""📊 <b><u>{texts[lang]['main']}</u></b>

{texts[lang]['count']}: <b>{count}</b>
"""


def msg_market_stats(user_id: int, market: MARKETS_TYPE, stats: CalculatorStats):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Статистика',
            'all': 'Всего расчетов',
            'tp': 'Тейк-профит',
            'sl': 'Стоп-лосс',
            'saved': 'Сохраненных',
            'sum': 'Сумма',
            'pieces': 'шт.',
            'max_profit': 'Крупный профит',
            'min_loss': 'Крупный убыток',
        },
        'en': {
            'name': 'Stats',
            'all': 'Total calculations',
            'tp': 'Take-profit',
            'sl': 'Stop-loss',
            'saved': 'Saved',
            'sum': 'Summury',
            'pieces': 'pieces',
            'max_profit': 'Large profit',
            'min_loss': 'Large loss',
        }
    }

    return f"""📊 <b>{texts[lang]['name']}</b> - <u><b>{market_translates[lang][market]}</b></u>

{POINT} {texts[lang]['all']}: <b>{stats.all_stats_count} {texts[lang]['pieces']}</b>

{POINT} {texts[lang]['saved']}: <b>{stats.saved_stats_count} {texts[lang]['pieces']}</b>
{POINT} {texts[lang]['tp']}: <b>{stats.tp_count}</b>
{POINT} {texts[lang]['sl']}: <b>{stats.sl_count}</b>

{POINT} {texts[lang]['max_profit']}: <b>{get_print_float(stats.max_profit, 3)} {stats.currency}</b>
{POINT} {texts[lang]['min_loss']}: <b>{get_print_float(stats.min_loss, 3)} {stats.currency}</b>

{POINT} {texts[lang]['sum']}: <b>{get_print_float(stats.profit, 3)} {stats.currency}</b>
"""


def msg_freeze_calc(user_id: int, risk_value: float, currency='', is_percent=False):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            '1': 'Вы превысили суточный процент риска на',
            '2': 'Желаете приостановить торговлю на некоторое время?',
            'end': 'На это время расчеты в калькуляторе невозможно будет совершать для безопасности Вашей торговли',
        },
        'en': {
            '1': 'You have exceeded the daily percentage of risk by',
            '2': 'Would you like to suspend trade for a while?',
            'end': 'At this time, calculations in the calculator cannot be made for the safety of your trade',
        }
    }

    if is_percent:
        risk_show = f'<b>{get_print_float(risk_value)}%</b> от депозита'
    else:
        risk_show = f'<b>{get_print_float(risk_value)} {currency}</b>'

    return f"""⚠️ {texts[lang]['1']} {risk_show}.
<b>{texts[lang]['2']}</b>

{get_freeze_annotation(lang)}

{texts[lang]['end']}.
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


def msg_frozen(user_id: int, datetime: str):
    lang = get_lang(user_id)

    text = {
        'ru': 'Калькулятор заморожен до',
        'en': 'The calculator is frozen until',
    }

    return f'❄️ {text[lang]} <b>{datetime}</b>'


# Ошибки ввода данных
def msg_trading_style_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите стиль текстом',
        'en': 'Enter the trading style in text'
    }

    return f'❗️ {texts[lang]}:'


def msg_freeze_error(user_id: int):
    lang = get_lang(user_id)

    text = {
        'ru': 'Неверный формат',
        'en': 'Wrong format',
    }

    return f"""❗️ {text[lang]}
{get_freeze_annotation(lang)}
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


def msg_digit_error(user_id: int, value_from: int | None = None, value_to: int | None = None):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Введите значение числом',
            'from': 'от',
            'to': 'до',
        },
        'en': {
            'main': 'Enter the value as a number',
            'from': 'from',
            'to': 'to',
        },
    }

    from_txt = ''
    to_txt = ''
    if value_from is not None:
        from_txt = f' {texts[lang]["from"]} {value_from}'

    if value_to is not None:
        to_txt = f' {texts[lang]["to"]} {value_to}'

    return f'❗️ {texts[lang]["main"]}{from_txt}{to_txt}:'


def msg_text_error(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите значение текстом',
        'en': 'Enter the value as a text'
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
        'ru': 'Цена стоп-лосса и входа равны',
        'en': 'The price of the stop-loss and entry are equal'
    }

    return f'⚠️ {texts[lang]}:'


def msg_currency_error(user_id: int, type: Literal['', 'not_found'] = ''):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'enter': 'Введите валюту текстом',
            'not_found': 'Валюта не найдена'
        },
        'en': {
            'enter': 'Enter the currency with text',
            'not_found': 'The currency is not found'
        }
    }

    error_mes = ''
    if type == 'not_found':
        error_mes = texts[lang]['not_found']

    return f"""{error_mes}
❗️ {texts[lang]['enter']}:
"""


def msg_splitting_error(user_id: int, error: Literal['digit', 'sum']):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'digit': 'Введите процент в виде числа',
            'sum': 'Суммарный процент превысил 100',
        },
        'en': {
            'digit': 'Enter the percent as a number',
            'sum': 'The total percent exceeded 100',
        }
    }

    return f'❗️ <i>{texts[lang][error]}</i>'


# Калькулятор
def msg_calculate(bot: TeleBot, user_id: int, chat_id: int):
    lang = get_lang(user_id)

    with bot.retrieve_data(user_id, chat_id) as data:
        updated_risk = data.get('updated_risk') or 1.
        type = data.get('calc_type')
        ticker = data.get('ticker')
        open_price = data.get('open_price')
        forex: ForexInfo | None = data.get('forex')
        tool: str = data.get('tool') or ''
        deposit: float | None = data.get('deposit')
        risk: tuple[float, bool] | None = data.get('risk')
        currency: str | None = data.get('currency')
        trading_type: str = data.get('trading_type', 'margin')

    risk_value = risk[0] if (risk is not None) else None
    if (risk is not None) and risk[1] and (deposit is not None):
        risk_value = risk[0] * deposit * 0.01 * updated_risk

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
            'pair': 'Валютная пара',

            'trading_type': 'Тип торговли',
            'margin': 'маржинальный',
            'spot': 'спотовый',
        },
        'en': {
            'ticker': 'Ticker',
            'dep': 'Deposit',
            'risk': 'Deal risk',
            'open': 'Entry price',
            'pair': 'Currency pair',

            'trading_type': 'Trading type',
            'margin': 'margin',
            'spot': 'spot',
        }
    }

    pair = '/'.join(forex.pair) if (forex is not None) else ''
    text = ''

    if type == 'forex' and pair != '':
        text += f'<b><u>{pair}</u></b>\n'
    elif type == 'crypto' and tool != '':
        text += f'<b><u>{tool}</u></b>\n'

    text += f'\n<b>{point[lang]["trading_type"]}</b>: {point[lang][trading_type]}\n'

    for el in type_list:
        item = vars_dict[el]
        if item is not None:
            if item == 'ticker':
                text += f'<b>{point[lang][el]}</b>: {item}\n'
            else:
                text += ''.join((
                    f'<b>{point[lang][el]}</b>: ',
                    f'{item} ',
                    (currency or '') if (
                        type != 'forex' or forex is None) else forex.pair[1],
                    '\n'
                ))

    text += '\n'

    return text


def msg_calculate_result(
    user_id: int,
    calc: Calculation,
    stats: CalculatorStats | None = None
):
    if calc.market == 'forex' and calc.forex_info is not None:
        return msg_calculate_forex_result(user_id, calc, stats)
    else:
        return msg_calculate_crypto_rf_usa_result(user_id, calc, stats)


def msg_calculate_crypto_rf_usa_result(
    user_id: int,
    calc: Calculation,
    stats: CalculatorStats | None = None
):
    lang = get_lang(user_id)

    point = {
        'ru': {
            'dep': 'Депозит' if stats is None else 'Итоговый депозит',
            'risk': 'Риск на сделку',
            'open': 'Цена',
            'sl': 'Стоп',
            'conclusion': 'Тейк-профит',
            'buy': 'Купите' if stats is None else 'Было куплено',
            'style': 'Стиль торговли',
            'trading_type': 'Тип торговли',
            'tool': 'Инструмент',
            'profit': 'Прибыль',
            'coin': 'монет',
            'paper': 'акций',

            'margin': 'маржинальный',
            'spot': 'спотовый',
        },
        'en': {
            'dep': 'Deposit' if stats is None else 'Final deposit',
            'risk': 'Deal risk',
            'open': 'Price',
            'sl': 'Stop',
            'conclusion': 'Take-profit',
            'buy': 'Buy' if stats is None else 'Bought',
            'style': 'Trading style',
            'trading_type': 'Trading type',
            'tool': 'Tool',
            'profit': 'Profit',
            'coin': 'coins',
            'paper': 'papers',

            'margin': 'margin',
            'spot': 'spot',
        }
    }

    if calc.market == 'crypto':
        tool_name = point[lang]["coin"]
    else:
        tool_name = point[lang]["paper"]

    trading_style = ''
    if calc.trading_style is not None:
        trading_style = f'<b>{point[lang]["style"]}</b>: {calc.trading_style.capitalize()}\n'

    # Округление
    round_count = calc.round_count or 5
    price_round_count = max(
        get_decimal_count(calc.open_price),
        get_decimal_count(calc.stop_loss),
        round_count
    )

    # Кол-во и сумма покупки
    count_bet, value_bet, _ = get_count_value_bet(calc)

    if calc.open_price > calc.stop_loss:
        long_short = '✅ Long'
    else:
        long_short = '🔻 Short'

    if stats is not None:
        profit_result = msg_calculate_saved_result(user_id, calc, stats)
        saved_mes = '#saved '
    else:
        saved_mes = ''

        p_show = ''
        conclusion = ''
        for i in range(len(calc.tp_ratio)):
            tp_ratio = calc.tp_ratio[i]

            take_profit = max(
                calc.open_price + tp_ratio *
                (calc.open_price - calc.stop_loss),
                0
            )

            conclusion += f'  <u>{get_print_float(take_profit, price_round_count)} {calc.currency}</u> (x{tp_ratio})'

            rate = 1
            if calc.split_values is not None and len(calc.split_values) != 0:
                percent = calc.split_values[i]
                rate = percent / 100

                count = count_bet * rate

                conclusion += f' (<b>{get_print_float(count, 2)} {tool_name}</b>) — {get_print_float(percent, round_count)}%'
                if i != len(calc.tp_ratio) - 1:
                    conclusion += f'\n'
            else:
                if i != len(calc.tp_ratio) - 1 and i % 2 == 1:
                    conclusion += f'\n'

            p_show += f'{get_print_float(abs(calc.open_price - take_profit) * rate * count_bet, round_count)}'

            if i != len(calc.tp_ratio) - 1:
                p_show += ' / '

        profit_result = f"""<b>{point[lang]['conclusion']}</b>:
{conclusion}

<b>{point[lang]["profit"]} ({calc.currency})</b>:
{TAB}{p_show}"""

    return f"""#<b><u>{(calc.tool or 'BTCUSDT').replace('/', '').upper()}</u></b> {saved_mes} - <b>{market_translates[lang][calc.market]}</b>

<b>{point[lang]["buy"]}</b>: {get_print_float(count_bet)} {tool_name}

<b>{point[lang]["open"]}</b>: {get_print_float(calc.open_price, price_round_count)} {calc.currency}
<b>{point[lang]["sl"]}</b>: {get_print_float(calc.stop_loss, price_round_count)} {calc.currency}
{profit_result}

<b>{point[lang]["dep"]}</b>: {get_print_float(calc.deposit+ ((calc.profit or 0.) if stats is not None else 0.))} {calc.currency}
<b>{point[lang]['risk']}</b>: {get_print_float(calc.risk_value)} {calc.currency}

<b>{point[lang]["trading_type"]}</b>: {point[lang][calc.trading_type]}
{trading_style}
"""


def msg_calculate_forex_result(
    user_id: int,
    calc: Calculation,
    stats: CalculatorStats | None = None
):
    if calc.forex_info is None:
        return 'Ошибка'

    pair = '/'.join(calc.forex_info.pair)

    lang = get_lang(user_id)

    point = {
        'ru': {
            'dep': 'Депозит' if stats is None else 'Итоговый депозит',
            'risk': 'Риск на сделку',
            'open': 'Цена',
            'sl': 'Стоп',
            'conclusion': 'Тейк-профит',
            'buy': 'Купить' if stats is None else 'Было куплено',
            'sum': 'Сумма',
            'style': 'Стиль торговли',
            'trading_type': 'Тип торговли',
            'profit': 'Прибыль',
            'lot': 'лота',

            'margin': 'маржинальный',
            'spot': 'спотовый',
        },
        'en': {
            'dep': 'Deposit' if stats is None else 'Final deposit',
            'risk': 'Deal risk',
            'open': 'Price',
            'sl': 'Stop',
            'conclusion': 'Take-profit',
            'buy': 'Buy' if stats is None else 'Bought',
            'sum': 'Sum',
            'style': 'Trading style',
            'trading_type': 'Trading type',
            'profit': 'Profit',
            'lot': 'lots',

            'margin': 'margin',
            'spot': 'spot',
        }
    }

    trading_style = ''
    if calc.trading_style is not None:
        trading_style = f'<b>{point[lang]["style"]}</b>: {calc.trading_style.capitalize()}\n'

    # Валюта торговли
    trading_currency = calc.forex_info.pair[1]

    # Округление
    round_count = calc.round_count or 5
    price_round_count = max(
        get_decimal_count(calc.open_price),
        get_decimal_count(calc.stop_loss),
        round_count
    )

    # Кол-во и сумма покупки
    count_bet, value_bet, _ = get_count_value_bet(calc)

    if calc.open_price > calc.stop_loss:
        long_short = '✅ Long'
    else:
        long_short = '🔻 Short'

    if stats is not None:
        profit_result = msg_calculate_saved_result(user_id, calc, stats)
        saved_mes = '#saved '
    else:
        saved_mes = ''

        p_show = ''
        conclusion = ''
        for i in range(len(calc.tp_ratio)):
            rate = 1
            tp_ratio_i = calc.tp_ratio[i]
            tp_i = max(
                calc.open_price + (calc.open_price -
                                   calc.stop_loss) * tp_ratio_i,
                0
            )

            conclusion += f'  <u>{get_print_float(tp_i, price_round_count)} {trading_currency}</u> (x{tp_ratio_i})'

            if calc.split_values is not None and len(calc.split_values) != 0:
                percent = calc.split_values[i]
                rate = percent / 100

                count = get_print_float(count_bet * rate, 4)

                conclusion += f' (<b>{count} {point[lang]["lot"]}</b>) — {get_print_float(percent, round_count)}%'
                if i != len(calc.tp_ratio) - 1:
                    conclusion += '\n'
            else:
                if i % 2 == 1:
                    conclusion += '\n'

            profit = abs(calc.open_price - tp_i) * \
                rate * count_bet * pow(10, 5)
            if calc.forex_info.pair[0] == calc.currency:
                profit /= calc.stop_loss
            elif calc.forex_info.pair[1] != calc.currency:
                profit /= calc.forex_info.cross_prices.get(
                    f'{calc.currency}/{calc.forex_info.pair[1]}', 1
                )

            p_show += f'{get_print_float(profit, round_count)}'
            if i != len(calc.tp_ratio) - 1:
                p_show += ' / '

        profit_result = f"""<b>{point[lang]['conclusion']}</b>:
{conclusion}

<b>{point[lang]["profit"]} ({calc.currency})</b>:
{TAB}{p_show}"""

    return f"""
#<b><u>{pair.replace('/', '').upper()}</u></b> {saved_mes} - <b>{market_translates[lang][calc.market]}</b>

<b>{point[lang]["buy"]}</b>: {get_print_float(count_bet, 4)} {point[lang]["lot"]}

<b>{point[lang]["open"]}</b>: {get_print_float(calc.open_price, price_round_count)} {calc.forex_info.pair[1]}
<b>{point[lang]["sl"]}</b>: {get_print_float(calc.stop_loss, price_round_count)} {calc.forex_info.pair[1]}
{profit_result}

<b>{point[lang]["dep"]}</b>: {get_print_float(calc.deposit + ((calc.profit or 0.) if stats is not None else 0.))} {calc.currency}
<b>{point[lang]['risk']}</b>: {get_print_float(calc.risk_value)} {calc.currency}

<b>{point[lang]["trading_type"]}</b>: {point[lang][calc.trading_type]}
{trading_style}
"""


def msg_calculate_saved_result(user_id: int, calc: Calculation, stats: CalculatorStats):
    lang = get_lang(user_id)

    point = {
        'ru': {
            'sum': 'Профит от сделки',
            'takes': 'Тейки',
            'stops': 'Стопы',
        },
        'en': {
            'sum': 'Deal profit',
            'takes': 'Take-profits',
            'stops': 'Stop-losses',
        },
    }

    profit = calc.profit or 0.

    return f"""<b>{point[lang]['sum']}: </b>{get_print_float(profit, calc.round_count)} {calc.currency}

<b>{point[lang]['takes']}</b>: {stats.tp_count}
<b>{point[lang]['stops']}</b>: {get_print_float(stats.sl_count)}"""


def msg_calculate_delete(user_id: int, prev_message: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Хотите удалить расчёт',
        'en': 'Do you want to delete the calculation',
    }

    return f"""{prev_message.strip()}

{TAB}<b>{texts[lang]}</b>?"""


def msg_calculate_change(user_id: int, prev_message: str):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Что хотите изменить',
        'en': 'What do you want to change',
    }

    return f"""{prev_message.strip()}

{TAB}<b>{texts[lang]}?</b>"""


# Ввод данных
def msg_enter_save_calc(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Как вы закрыли данную сделку?',
        'en': 'How did you close this deal?',
    }

    return texts[lang]


def msg_enter_calc_image(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Загрузите свой скриншот сделки и он останется в чате навсегда',
        'en': 'Upload your screenshot of the deal and it will stay in the chat'
    }

    return f'👉 {texts[lang]}'


def msg_enter_take_profit(user_id: int, tp_ratio: list[int]):
    lang = get_lang(user_id)

    current_tp = tp_ratio.copy()
    current_tp.sort()

    tp_count = len(current_tp)

    max_count = 5
    texts = {
        'ru': {
            'name': 'Установка тейк-профита',
            'current': 'Текущий выбор',
            'max': 'Учитывайте, что максимальный коэффициент тейк-профита',
            'max_count': f'Можно выбрать до <b>{max_count}</b> значений',
            '1': 'Выберите <b>первое</b> значение',
            'action': 'Выберите действие',
            'next': 'Выберите <b>следующее</b> значение',
        },
        'en': {
            'name': 'Installation of a teke-profit',
            'current': 'Current choice',
            'max': 'Keep in mind that the maximum take-profit coefficient',
            'max_count': f'You can choose before <b>{max_count}</b> meanings',
            '1': 'Select <b>the first</b> meaning',
            'action': 'Choose an action',
            'next': 'Select the <b>following</b> meaning',
        },
    }

    text = f'<u>{texts[lang]["name"]}</u>\n'

    if tp_count != 0:
        text += f'{texts[lang]["current"]}: <b>'

        for el in current_tp:
            text += f'x{el} '

        text += '</b>\n'

    text += f'\n{texts[lang]["max"]} - <b>x10</b>\n'
    text += f'{texts[lang]["max_count"]}\n\n'

    if tp_count == 0:
        text += f'{texts[lang]["1"]}'
    elif tp_count == 5:
        text += f'{texts[lang]["action"]}'
    else:
        text += f'{texts[lang]["next"]}'

    return text


def msg_enter_splitting(user_id: int, tp_ratio: list[int], split: list[float], is_last=False):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Установка разделения профита',
            'current': 'Текущий выбор',
            'percent_sum': 'Суммарный процент',
            'last': 'Оставшиеся',
            'split': 'торговой позиции можно разбить',
            'info': 'Разбиение расчитает каждую из <i>n</i> частей для слудующих +1 тейк-профитов\nВыберите на <u>сколько частей</u> разделить остаток',
            '1': 'Выберите <b>первое</b> значение тейк-профита',
            'action': 'Выберите действие',
            'tp': 'Введите <b>процент вывода</b> для тейк-профита',
            'next': 'Выберите <b>следующее</b> значение тейк-профита',
        },
        'en': {
            'name': 'Installation of the separation of profit',
            'current': 'Current choice',
            'percent_sum': 'The total percentage',
            'last': 'Remaining',
            'split': 'of trading position can be defeated',
            'info': 'Splitting calculates each of the <i>n</i> parts for the mining +1 teak profits\nSelect <u> how many parts </u> divide the balance',
            '1': 'Select <b> the first </b> take-profit value',
            'action': 'Choose an action',
            'tp': 'Enter the <b> percentage of the output </b> for the take profite',
            'next': 'Select <b>the following</b> Take-profite value',
        },
    }

    tp_count = len(tp_ratio)
    split_count = len(split)

    if tp_count == 0 or split_count == 0:
        sorted_tp, sorted_split = [], []
    else:
        sorted_tp, sorted_split = zip(*sorted(zip(tp_ratio, split)))

    percents_sum = sum(split)
    if abs(percents_sum - 100) < 0.2:
        percents_sum = 100

    text = f'<u>{texts[lang]["current"]}</u>\n'

    if tp_count != 0 and split_count != 0:
        text += f'\n<u>{texts[lang]["name"]}</u>: <b>\n'

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
        text += f'<i>{texts[lang]["percent_sum"]}:</i> <b>{get_print_float(percents_sum)}</b>\n'

    text += '\n'
    if is_last:
        text += f'{texts[lang]["last"]} <b>{get_print_float(100-percents_sum, 2)}%</b> {texts[lang]["split"]}. '
        text += texts[lang]["info"]
    elif tp_count == 0:
        text += texts[lang]['1']
    elif tp_count == 5 or percents_sum == 100:
        text += texts[lang]['action']
    elif tp_count != split_count:
        text += f'{texts[lang]["tp"]} <b>x{tp_ratio[-1]}</b>'
    else:
        text += texts[lang]["next"]

    return text


def msg_enter_trading_type(user_id: int):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'main': 'Типы торговли',
            'm': '<b>Маржинальный</b>: расчеты будут производиться, включая кредитные плечи',
            's': '<b>Спотовый</b>: расчеты производятся, исходя из фиксированного депозита',
            'enter': 'Выберите тип'
        },
        'en': {
            'main': 'Trading types',
            'm': '<b>Margin</b>: calculations will be made, including leverage',
            's': '<b>Spot</b>: calculations are made based on a fixed deposit',
            'enter': 'Choose type'
        },
    }

    return f"""<b><u>{texts[lang]['main']}</u></b>
{texts[lang]['m']}

{texts[lang]['s']}

👇 {texts[lang]['enter']}:"""


def msg_enter_summury_profit_type(user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        return """Выберите вид разделения суммы:

<i>*Простой - без деления профита, продажа 100% торговой позиции
*Разделение - продажа торговой позиции разделяется на несколько тейк-профитов</i>"""
    else:
        return """Select the type of division of the amount:

<i>*Simple - without division of profit, sale 100% of the trading position
*Separation - the sale of a trading position is divided into several take profites </i>"""


def msg_enter_tool(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Введите Ваш инструмент',
        'en': 'Enter Your tool'
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
        'ru': {
            'main': 'Введите <u>риск на день</u>',
            'desc1': '"<b>Риск на день</b>" - процент или сумма капитала, превышая которую, система будет напоминать об этом.',
            'desc2': 'Трейдинг строится на систематической торговле, и риски на день/неделю/месяц нужно контролировать',
        },
        'en': {
            'main': 'Enter <u>daily risk</u>',
            'desc1': '"<b>Daily risk</b>" - the percentage or amount of capital exceeding which the system will remind you about it.',
            'desc2': 'Trading is based on systematic trading, and the risks for the day/week/month need to be controlled',
        },
    }

    return f""" {texts[lang]['desc1']}
{texts[lang]['desc2']}

✍ {texts[lang]['main']}
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

    return f"""✍ {texts[lang]['choose']}.
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
        text = 'Введите цену стоп-лосса:'
    else:
        text = 'Enter the stop-loss price'

    return f'✍ {text}'


def msg_enter_profit_minus(user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        text = 'Введите <b>убыток</b> по этой сделке:'
    else:
        text = 'Enter <b>loss</b> of this deal:'

    return f'✍ {text}'


def msg_enter_profit_sum(user_id: int):
    lang = get_lang(user_id)

    if lang == 'ru':
        text = 'Введите <b>профит</b> по этой сделке:'
    else:
        text = 'Enter <b>profit</b> of this deal:'

    return f'✍ {text}'


def msg_choose_lang(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Выберите язык',
        'en': 'Choose language'
    }

    return f'🌐 {texts[lang]}'


def msg_update_deposit(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'main': 'Хотите изменять свой депозит при сохранении расчета?'
        },
        'en': {
            'main': 'Do you want to change your deposit after saving the calculation?'
        },
    }

    return texts[lang]['main']


def msg_confirm_reset(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Вы действительно хотите <b>сбросить</b> все настройки',
        'en': 'Do you really want to <b>drop</b> all settings',
    }

    return f'⚠️ {texts[lang]}?'


def msg_calculation_saved(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Расчет сохранен',
        'en': 'The calculation is saved',
    }

    return f'✅ {texts[lang]}!'


def msg_calculation_deleted(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': 'Расчёт удалён',
        'en': 'Calcultaion deleted'
    }

    return f'⭕️ {texts[lang]}!'


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
