

from common.dt import get_datetime_now, get_str_by_datetime
from models import LANGUAGES_TYPE


def msg_violation(lang: LANGUAGES_TYPE, current: int, isToday: bool, messages: list[dict[str, str]], is_edit: bool):
    texts = {
        'ru': {
            'main': 'Нарушения',
            'info': """Отмечайте, нарушали ли правила сегодня.
Если не нарушали, получите <b>5 баллов</b> за день.
В течение месяца Вы можете набрать до <b>150 баллов</b>.""",
            'edit': 'Изменять статус можно <b>4 раза</b> в месяц.',
            'current': 'За текущий месяц',
            'point': 'баллов',
            'today': 'Сегодня:',

            'True': 'нарушил',
            'False': 'не нарушил',
            'None': 'не торговал',
        },
        'en': {
            'main': 'Violations',
            'info': """Mark if the rules have violated today.
If you are not violated, get <b>5 points</b> per day.
Within a month you can score up to <b>150 points</b>.""",
            'edit': 'You can change the status <b>4 times</b> per month.',
            'current': 'For the current month',
            'point': 'points',
            'today': 'Today:',

            'True': 'violated',
            'False': 'no violate',
            'None': 'no trade',
        },
        'uz': {
            'main': 'Qoidabuzarliklar',
            'info': 'Siz bugun qoidabuzarlik qilganligingizni belgilash imkoniyatiga egasiz. Agar siz qoidabuzarlik qilmagan bo\'lsangiz, buni belgilang va kun uchun 5 ball olasiz. Oy davomida siz maksimal 150 ball to\'plashingiz mumkin.',
            'edit': 'Siz oyiga <b>4 marta</​​b> holatini o\'zgartirishingiz mumkin.',
            'current': 'Joriy oy uchun',
            'point': 'ballar',
            'today': 'Bugun:',

            'True': 'buzilgan',
            'False': 'buzilmagan',
            'None': 'savdo yo\'q',
        },
        'tr': {
            'main': 'İhlaller',
            'info': 'Bugün kuralları ihlal edip etmediğinizi işaretleyebilirsiniz. Eğer kuralları ihlal etmediyseniz, bunu işaretleyin ve gün için 5 puan kazanın. Ay boyunca maksimum 150 puan kazanabilirsiniz.',
            'edit': 'Ayda <b>4 kez</b> durumunu değiştirebilirsiniz.',
            'current': 'Mevcut ay için',
            'point': 'puan',
            'today': 'Bugün:',

            'True': 'ihlal edilen',
            'False': 'ihlal etmek yok',
            'None': 'ticaret Yok',
        }
    }

    months = {'ru': [
        'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
        'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'
    ], 'en': [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]}

    mes = ''
    for el in messages:
        mes += f'\n<b>{el.get("date")}</b>'
        status = str(el.get("status"))

        points = 5 if status == 'False' else 0 if status == 'True' else 1
        mes += f' - {texts[lang][status]} ({points})'

    current_date = get_str_by_datetime(get_datetime_now(), "day.month")
    month = ('За' if lang == 'ru' else 'For') + ' ' + \
        months[lang][int(current_date.split('.')[1]) - 1]

    return f"""<b>{texts[lang]['main']} - {current_date}</b>""" \
        + (f"""\n\n{texts[lang]['info']}""" if not isToday else '') \
        + (f"""\n\n{texts[lang]['edit']}""" if is_edit else '') \
        + f"""\n\n<b>{month}</b>: {current}/150 {texts[lang]['point']}
{mes}

{texts[lang]['today'] if not isToday else ''}"""


def msg_violation_message(lang: LANGUAGES_TYPE):
    texts = {
        'ru': 'Можете описать нарушение и прикрепть фото',
        'en': 'You can describe the violation and attach a photo',
        'uz': 'Siz qoidabuzarlikni tasvirlashingiz va fotosuratni biriktirishingiz mumkin',
        'tr': 'İhlali tanımlayabilir ve bir fotoğraf ekleyebilirsiniz',
    }

    return texts[lang]

