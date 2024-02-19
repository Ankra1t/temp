from telebot import TeleBot
from common.utils import float_to_print, get_decimal_count, get_lang, get_print_float

from db_new import db_new


BULLET = '✦'

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

    return '\n'.join((
        f'⚡️ <b><u>{texts[lang]["name"]}</u></b>',
        '',
        f'1. <b>{texts[lang]["1"]}</b>',
        f'2. <b>{texts[lang]["2"]}</b>',
        '',
        msg_uses_count(user_id, uses_count)
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

    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    base = db_new.get_user_base(user_db_id)
    deposit, risk, currency = (
        base.get('base_deposit'),
        base.get('base_risk_percent'),
        base.get('base_currency') or 'USD'
    )

    risk_is_percent = db_new.get_user_risk_is_percent(user_db_id)
    tp_ratio = db_new.get_calculator_tp_ratio(user_db_id)
    market: str = db_new.get_calculator_user_market(user_db_id) or 'crypto'

    texts = {
        'ru': {
            'name': 'Настройки',
            'dep': 'Базовый депозит',
            'risk': 'Базовый риск',
            'currency': 'Базовая валюта',
            'tp_show': 'Вывод расчета прибыли',
            'market': 'Рынок',
        },
        'en': {
            'name': 'Settings',
            'dep': 'Default deposit',
            'risk': 'Default risk',
            'currency': 'Default currency',
            'tp_show': 'Display calculation of profit',
            'market': 'Market',
        },
    }

    tp_result = ''
    for el in tp_ratio:
        tp_result += f'x{el} '

    return '\n'.join((
        f'⚙️ <b><u>{texts[lang]["name"]}</u></b>',
        '',
        (
            f'{BULLET} {texts[lang]["dep"]}: <b>'
            f'{f"{float_to_print(deposit)} {currency}" if deposit is not None else "-"}'
            '</b>'
        ),
        (
            f'{BULLET} {texts[lang]["risk"]}: <b>'
            f'{f"{float_to_print(risk)}" if risk is not None else ""}'
            f'{"-" if risk is None else "%" if risk_is_percent else f" {currency}"}'
            '</b>'
        ),
        '',
        f'{BULLET} {texts[lang]["tp_show"]}: <b>{tp_result}</b>',
        f'{BULLET} {texts[lang]["market"]}: <b>{market_translates[lang][market]}</b>'
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


def msg_settings_set_tp_show(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    tp_ratio = db_new.get_calculator_tp_ratio(user_db_id)

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Установка расчета прибыли',
            'now': 'Сейчас выводится',
            'note': 'При изменении данных значений выключается разделение прибыли'
        },
        'en': {
            'name': 'Settings',
            'subname': 'Set calculation of profit',
            'now': 'Now displayed',
            'note': 'When these values changes, the division of profit is turned off'
        }
    }

    result = ''
    for el in tp_ratio:
        result += f'x{el} '

    return '\n'.join((
        f'⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>',
        f'{texts[lang]["note"]}',
        '',
        f'{texts[lang]["now"]}: <b>{result}</b>'
    ))


def msg_split_settings(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    is_splitting = db_new.get_user_is_splitting(user_db_id)
    split_values = db_new.get_user_split_values(user_db_id)

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Разделение профита',
            'split': 'Разделение',
            'on': 'Включено',
            'off': 'Выключено',
        },
        'en': {
            'name': 'Settings',
            'subname': 'Profit splitting',
            'split': 'Splitting',
            'on': 'Turned on',
            'off': 'Turned off',
        }
    }

    on_off = 'on' if is_splitting else 'off'

    splitting = ''

    if len(split_values) != 0:
        splitting = 'Разделение: '
        for el in split_values:
            splitting += f'{el}% '

    return '\n'.join((
        f'⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>',
        '',
        f'<b>{texts[lang][on_off]}</b>',
        '',
        splitting,
    ))


def msg_summury_profit_settings(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    tp_ratio = db_new.get_calculator_tp_ratio(user_db_id)
    is_splitting = db_new.get_user_is_splitting(user_db_id)
    split_values = db_new.get_user_split_values(user_db_id)

    texts = {
        'ru': {
            'name': 'Настройки',
            'subname': 'Вывод профита',
            'take_profit': 'Ваш тейк профит',
            'split': 'Разделение',
            'on': 'включено',
            'off': 'выключено',
        },
        'en': {
            'name': 'Settings',
            'subname': 'Summury profit',
            'take_profit': 'Your take profit',
            'split': 'Splitting',
            'on': 'turned on',
            'off': 'turned off',
        }
    }

    info_result = ''

    if is_splitting:
        for i, el in enumerate(tp_ratio):
            info_result += f'<b>x{el} ({split_values[i]}%)</b>'

            if i == len(tp_ratio) - 1:
                pass
            elif i % 3 != 2:
                info_result += ' - '
            else:
                info_result += '\n'
    else:
        info_result = f'{texts[lang]["take_profit"]}: '
        for i, el in enumerate(tp_ratio):
            info_result += f'<b>x{el}</b>'
            if i != len(tp_ratio) - 1:
                info_result += ' - '

    return '\n'.join((
        f'⚙️ <b>{texts[lang]["name"]}</b> > <b><u>{texts[lang]["subname"]}</u></b>',
        '',
        f'{texts[lang]["split"]}: <b>{texts[lang]["on" if is_splitting else "off"]}</b>',
        f'{info_result}',
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

    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    base_value = db_new.get_user_base(user_db_id)
    risk_is_percent = db_new.get_user_risk_is_percent(user_db_id)

    deposit: float | None = base_value.get('base_deposit')
    risk: float | None = base_value.get('base_risk_percent')
    currency: str = base_value.get('base_currency') or 'USD'

    if risk_is_percent and (deposit is not None) and (risk is not None):
        risk *= deposit * 0.01

    with bot.retrieve_data(user_id, chat_id) as data:
        type = data.get('calc_type')
        ticker = data.get('ticker')
        open_price = data.get('open_price')

    type_list = ['ticker', 'dep', 'risk', 'open']
    vars_dict = {
        'ticker': ticker,
        'dep': deposit,
        'risk': risk,
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
    open_price: float,
    stop_loss: float,
    count_bet: float,
    value_bet: float,
    credit: int,
    risk_value: float,
    take_profit: list[float],
    profit: list[float],
):
    lang = get_lang(user_id)
    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    currency: str = db_new.get_user_base(user_db_id)['base_currency'] or 'USD'
    is_splitting = db_new.get_user_is_splitting(user_db_id)
    split_values = db_new.get_user_split_values(user_db_id)

    point = {
        'ru': {
            'dep': 'Депозит',
            'open': 'Цена открытия',
            'sl': 'Стоп лосс',
            'tp': 'Тейк профит',
            'split': 'Разделение',
            'count': 'Приобретаем',
            'sum': 'Покупаем на',
            'credit': 'Кредитное плечо',
            'risk_val': 'Риск на сделку',
            'profit': 'Прибыль'
        },
        'en': {
            'dep': 'Deposit',
            'open': 'The open price',
            'sl': 'Stop loss',
            'tp': 'Take profit',
            'split': 'Split',
            'count': 'Purchase',
            'sum': 'Buy on',
            'credit': 'Leverage',
            'risk_val': 'The risk of a deal',
            'profit': 'Profit'
        }
    }

    round_count = max(
        get_decimal_count(open_price),
        get_decimal_count(stop_loss)
    )

    tp_show = ''
    split_show = ''
    p_show = ''
    for i in range(len(take_profit)):
        tp_show += f'{get_print_float(take_profit[i], round_count)} {currency}'
        p_show += f'{get_print_float(profit[i], round_count)} {currency}'

        if is_splitting:
            split_show += f'{get_print_float(split_values[i], round_count)}% '

        if i != len(take_profit) - 1:
            tp_show += ' / '
            p_show += ' / '

            if is_splitting:
                split_show += ' / '

    return '\n'.join([
        f'{BULLET} {point[lang]["dep"]}: <b>{get_print_float(deposit)} {currency}</b>',
        f'{BULLET} {point[lang]["risk_val"]}: <b>{get_print_float(risk_value)} {currency}</b>',
        '',
        f'{BULLET} {point[lang]["open"]}: <b>{get_print_float(open_price, round_count)} {currency}</b>',
        f'{BULLET} {point[lang]["sl"]}: <b>{get_print_float(stop_loss, round_count)} {currency}</b>',
        '',
        f'{BULLET} {point[lang]["count"]}: <b>{get_print_float(count_bet)} монет</b>',
        f'{BULLET} {point[lang]["sum"]}: <b>{get_print_float(value_bet)} {currency}</b>',
        f'{BULLET} {point[lang]["credit"]}: <b>{credit} к 1</b>',
        '',
        ''.join((
            f'{BULLET} {point[lang]["tp"]}: <b>{tp_show}</b>',
            f"\n{BULLET} {point[lang]['split']}: <b>{split_show}</b>" if split_show != '' else ''
        )),
        f'{BULLET} {point[lang]["profit"]}: <b>{p_show}</b>',
    ])


def msg_calculate_forex_result(
    user_id: int,
    deposit: float,
    val_dep: str,
    risk_percent: float,
    pair: str,
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
            'pair': 'Валютная пара',
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
            'pair': 'Currency pair',
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
        f'{BULLET} {point[lang]["pair"]}: <b>{pair}</b>',
        f'{BULLET} {point[lang]["open"]}: <b>{open_price}</b>',
        f'{BULLET} {point[lang]["sl"]}: <b>{stop_loss}</b>',
        f'{BULLET} {point[lang]["tp"]}: <b>{round(take_profit_1, 2)} / {round(take_profit_2, 2)} / {round(take_profit_3, 2)}</b>',
        f'{BULLET} {point[lang]["lot"]}: <b>{round(lot, 2)}</b>',
        '',
        f'{BULLET} {point[lang]["risk_val"]}: <b>{risk_value} {val_dep}</b>',
        f'{BULLET} {point[lang]["profit"]}: <b>{round(risk_value * 2, 2)} / {round(risk_value * 3, 2)} / {round(risk_value * 4, 2)}</b>'
    ])


# Ввод данных
def msg_enter_split(user_id: int):
    lang = get_lang(user_id)

    user_db_id = db_new.get_user_id_by_tg_id(user_id)
    tp_ratio = db_new.get_calculator_tp_ratio(user_db_id)

    if len(tp_ratio) == 3:
        example = '75 15 10'
    elif len(tp_ratio) == 2:
        example = '75 25'
    else:
        example = '100'

    tp_text = ''
    for i, el in enumerate(tp_ratio):
        tp_text += f'x{el}'
        if i != len(tp_ratio) - 1:
            tp_text += ' '

    return '\n'.join((
        f'Введите <b>проценты</b> разделения <u>через пробел</u> для каждого из тейк профитов',
        '',
        f'Ваши тейк профиты: <b>{tp_text}</b>',
        'Сумма процентов должна быть равна <b>100%</b>',
        '',
        f'Пример: <b>{example}</b>'
    ))


def msg_enter_take_profit(user_id: int, tp_ratio: list[int]):
    current_tp = tp_ratio.copy()
    current_tp.sort()

    tp_count = len(current_tp)

    text = '<u>Установка тейк профита</u>\n'

    if tp_count != 0:
        text += 'Текущий выбор: <b>'

        for el in current_tp:
            text += f'x{el} '

        text += '</b>\n'

    text += '\nУчитывайте, что максимальный коэффициент тейк профита - <b>x10</b>\n'
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
    if abs(percents_sum - 100) < 0.1:
        percents_sum = 100

    text = '<u>Установка разделения профита</u>\n'

    if tp_count != 0 and split_count != 0:
        text += '\n<u>Текущий выбор</u>: <b>\n'

        for i, el in enumerate(sorted_tp):
            try:
                percent = f'({sorted_split[i]}%)'
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
        text += f'<i>Сумма процентов:</i> <b>{percents_sum}</b>\n'

    text += '\n'
    if is_last:
        text += f'Оставшиеся <b>{round(100-percents_sum, 2)}%</b> торговой позиции можно разбить. '
        text += 'Разбиение расчитает каждую из <i>n</i> частей для слудующих +1 тейк профитов\n'
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
    return '\n'.join((
        'Выберите вид разделения суммы:',
        '',
        '<i>*Простой - вывод профита при продажы 100% торговой позиции',
        '*Разделение - вывод профита при разделении торговой позиции по нескольким тейк-профитам</i>'
    ))


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
        'ru': 'Введите <b>процент</b> риска от депозита <b>(со знаком %)</b> или сумму риска',
        'en': 'Enter the <b>percentage</b> of risk by deposit <b>(with a % sign)</b> or the risk amount'
    }

    return f'✍ {texts[lang]}:'


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
