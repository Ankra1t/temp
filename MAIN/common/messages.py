from CALCULATE.common.messages import POINT
from common.dt import get_datetime_now, get_str_by_datetime
from common.utils import get_lang, get_print_float
from models import Price, Purchase, UserInfo

from db import db


def default_menu(name: str):
    return f"""
<b>{name}</b>

Выберите:
"""


def msg_referral(user_id: int, ref_count: int, bot_name: str):
    lang = get_lang(user_id)
    user_db_id = db.get_user_id_by_tg_id(user_id)

    texts = {
        'ru': {
            '1': f'<b>Сейчас у вас:</b> {ref_count} реферал(ов)',
            '2': '<b>Скопируйте</b> ссылку ниже и поделитесь ей со своими друзьями',
            '3': 'В будущем Вы будете получать <b>вознаграждение</b> за активность ваших рефералов',
        },
        'en': {
            '1': f'<b>Now you have:</b> {ref_count} referral(s)',
            '2': '<b>Copy</b> the link below and share it with your friends',
            '3': 'In the future, you will receive <b>remuneration</b> for the activity of your referrals',
        },
    }

    return f"""{texts[lang]['1']}

{texts[lang]['2']}
{texts[lang]['3']}😉

<code>https://t.me/{bot_name}/?start={user_db_id}</code>
"""


def msg_referral_list(user_id: int, referrals: list[UserInfo]):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Ник',
            'sum': 'Всего потратил',
            'not': 'Рефералы не найдены',
        },
        'en': {
            'name': 'Nick',
            'sum': 'Spent',
            'not': 'Referrals not found',
        },
    }

    res = ''
    if len(referrals) != 0:
        for ref in referrals:
            name = f'@{ref.username}' if ref.username else '-'
            
            purchase = db.get_purchases_by_user(user_id)
            money = 0
            for el in purchase:
                money += el.sum or 0
            res += f"{POINT} {texts[lang]['name']}: {name}\n{texts[lang]['sum']}: <b>{money}</b>\n\n"
    else:
        res = f"{texts[lang]['not']} 😔\n"

    return res


def msg_site_login(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Вход на сайт',
            'click': 'Нажмите на кнопку для перехода на сайт',
            'time': 'Ссылка действует несколько минут',
        },
        'en': {
            'name': 'Site',
            'click': 'Press the button to go website',
            'time': 'The link is valid for several minutes',
        },
    }

    return f"""<b><u>{texts[lang]['name']}</u></b>

👇 {texts[lang]['click']}
<i>{texts[lang]['time']}</i>
"""


def msg_user_tariff(user_id: int, tariff: Price):
    discount = ''
    if tariff.discount is not None:
        now = get_datetime_now()
        fin_date_discount = tariff.discount.findate
        if fin_date_discount > now:
            discount = f'<b>Скидка {str(round(tariff.discount.percent))}%</b>'

    return f"""
{tariff.name}
{tariff.price} {tariff.currency}
{tariff.description}
<i>действует {tariff.duration_days} дн.</i>

{discount}
"""


def msg_admin_tariff(tariff: Price):
    discount = ''
    if tariff.discount is not None:
        now = get_datetime_now()
        if tariff.discount.findate > now:
            fin_date = get_str_by_datetime(tariff.discount.findate)
            discount = f'Скидка <b>{get_print_float(tariff.discount.percent, 2)}%</b> до {fin_date}'

    return f"""
{tariff.name}
<b>{get_print_float(tariff.price)} {tariff.currency}</b>
{tariff.description}

Продукт: <b>{tariff.type_product}</b>
Действует <b>{tariff.duration_days}</b> дней
""" + (f'\n{discount}' if discount != '' else '')


def msg_user_account(user_id: int, spent: float, refs: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Личный кабинет',
            'spent': 'Всего потратили',
            'refs': 'Рефералов',
        },
        'en': {
            'name': 'Profile',
            'spent': 'Spent',
            'refs': 'Referrals',
        },
    }

    return f"""<b><u>{texts[lang]['name']}</u></b>

{texts[lang]['refs']}: <b>{refs}</b>
"""
# {texts[lang]['spent']}: <b>{get_print_float(spent)}</b>


def msg_user_purchases(user_id: int, purchases: list[Purchase]):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'name': 'Мои покупки',
            'calc': 'Калькулятор',
            'signals': 'Рекомендации',
            'calc_signals': 'PRO',
            'date': 'Дата',
        },
        'en': {
            'name': 'My purchases',
            'calc': 'Calculator',
            'signals': 'Recommendations',
            'calc_signals': 'PRO',
            'date': 'Date',
        },
    }

    products = {'signals': '', 'calc': '', 'calc_signals': ''}
    for p in purchases:
        info = f'🛍 "<b>{p.price_name}</b>" <u>{p.sum}</u> {p.currency}'
        info += f'\n{texts[lang]["date"]} {get_str_by_datetime(p.payment_date or get_datetime_now())}\n'

        type_p = p.type_product or 'calc'

        prev = products[type_p]
        if prev != '':
            products[type_p] += '\n'
        products[type_p] += info

    result = f'<b><u>{texts[lang]["name"]}</u></b>\n'

    if len(purchases) == 0:
        result += '\n Нет покупок'
        return result

    if products['calc'] != '':
        result += f'\n{POINT} <b>{texts[lang]["calc"]}</b>\n'
        result += products['calc']

    if products['signals'] != '':
        result += f'\n{POINT} <b>{texts[lang]["signals"]}</b>\n'
        result += products['signals']

    if products['calc_signals'] != '':
        result += f'\n{POINT} <b>{texts[lang]["calc_signals"]}</b>\n'
        result += products['calc_signals']

    return result
