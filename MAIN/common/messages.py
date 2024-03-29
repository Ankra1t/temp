from common.dt import get_datetime_now
from models import Price


def default_menu(name: str):
    return f"""
<b>{name}</b>

Выберите:
"""


def msg_referral(ref_count: int, bot_name: str, user_id: int):
    return f"""
<b>Сейчас у вас:</b> {ref_count} реферал(ов)
<b>Скопируйте</b> ссылку ниже и поделитесь ей со своими друзьями😌
В будущем Вы будете получать <b>вознаграждение</b> за активность ваших рефералов😉

https://t.me/{bot_name}/?start={user_id}
"""


def msg_site_login():
    return f"""<b><u>Вход на сайт</u></b>

👇 Нажмите на кнопку для перехода на сайт
<i>Ссылка действует несколько минут</i>
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
