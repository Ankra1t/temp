from typing import Literal
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from CALCULATE.common.messages import market_translates
from common.keyboard import back_txt, cancel_txt
from common.utils import get_lang

from db import LANGUAGES_TYPE, db
from models import MARKETS_TYPE, Calculation
from services import calculation, channel_calc

from ..channel_post.keyboards import getButton as getChannelButton
from .filter import stats_factory


def getButton(text: str, type: str, stat_id=0, stats_market: MARKETS_TYPE = 'crypto', page=0):
    return InlineKeyboardButton(
        text, None,
        stats_factory.new(
            type=type,
            stat_id=stat_id,
            sm=stats_market,
            p=page,
        )
    )


def kb_stats(user_id: int, type: Literal['main', 'market'] = 'main', prev_market: MARKETS_TYPE | None = None):
    lang = get_lang(user_id)

    row_width = 2
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    buttons = []
    markets_list: tuple[MARKETS_TYPE, ...] = (
        'crypto', 'forex', 'RF', 'USA'
    )  # 'paper', 'future',
    for i, el in enumerate(markets_list):
        btn = getButton(
            market_translates[lang][el],
            'stats_market' if el != prev_market else '',
            -1, el
        )
        buttons.append(btn)

        if len(buttons) == row_width or (i + 1 == len(markets_list) and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    if type == 'main':
        btn_back = getButton(back_txt(lang), 'go_main')
    else:
        btn_back = getButton(back_txt(lang), 'go_stats')

    keyboard.add(btn_back)
    return keyboard


def kb_stats_page(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    texts = {
        'ru': {
            'list': 'Список',
            'list_wait': 'Список в ожидании',
            'list_done': 'Список выполненных',
            'list_canceled': 'Список отмененных',
        },
        'en': {
            'list': 'List',
            'list_wait': 'List in wait',
            'list_done': 'List done',
            'list_canceled': 'List canceled',
        },
        'uz': {
            'list': 'Roʻyxat',
            'list_wait': 'Kutilayotgan roʻyxat',
            'list_done': 'Bajarilgan roʻyxat',
            'list_canceled': 'Bekor qilingan roʻyxat',
        },
        'tr': {
            'list': 'Liste',
            'list_wait': 'Bekleyen liste',
            'list_done': 'Tamamlanan liste',
            'list_canceled': 'İptal edilen liste',
        },
    }

    keyboard.add(
        getButton(texts[lang]['list_wait'], 'list+wait'),
        getButton(texts[lang]['list_done'], 'list+done'),
        # getButton(texts[lang]['list_canceled'], 'list+canceled'),
        getButton(back_txt(lang), 'go_main'),
    )

    return keyboard


def kb_calc_list(user_id: int, page: int, count: int, list_type: str):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'start': 'В начало',
            'end': 'В конец',
            'next': 'Далее',
            'back': 'Назад',
        },
        'en': {
            'start': 'To the beginning',
            'end': 'To the end',
            'next': 'Next',
            'back': 'Back',
        },
        'uz': {
            'start': 'Boshiga',
            'end': 'Oxiriga',
            'next': 'Keyingi',
            'back': 'Orqaga',
        },
        'tr': {
            'start': 'Başa',
            'end': 'Sona',
            'next': 'Sonraki',
            'back': 'Geri',
        },
    }

    buttons = []

    keyboard = InlineKeyboardMarkup(row_width=3)

    if count > 1:
        btn_start = getButton(texts[lang]['start'],
                              f'list+{list_type}', page=0)
        btn_end = getButton(texts[lang]['end'],
                            f'list+{list_type}', page=count - 1)
        btn_next = getButton(texts[lang]['next'],
                             f'list+{list_type}', page=page + 1)
        btn_back = getButton(texts[lang]['back'],
                             f'list+{list_type}', page=page - 1)

        counter = getButton(f'{page + 1}/{count}', 'counter')

        if page == 0:
            buttons.append(btn_end)
        else:
            buttons.append(btn_back)

        buttons.append(counter)

        if page + 1 == count:
            buttons.append(btn_start)
        else:
            buttons.append(btn_next)

    keyboard.add(
        *buttons,
        getButton(back_txt(lang), 'go_stats')
    )
    return keyboard


def kb_calc_result(user_id: int, calc: Calculation, isResult=False):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    isAdmin = db.get_worker_role(user_db_id)
    send_data = channel_calc.getByCalc(calc.id)

    texts = {
        'ru': {
            'save': 'Сохранить в статистику',
            'del': 'Удалить',
            'change': 'Изменить',
            'img': 'Картинка и описание',
            'result': 'Результат',

            'deal': 'В сделке',
            'cancel_deal': 'Отмена сделки',
            'take': 'Тейк',
            'stop': 'Стоп',
            'breakeven': 'Безубыток',
        },
        'en': {
            'save': 'Save to stats',
            'del': 'Delete',
            'change': 'Change',
            'img': 'Picture and description',
            'result': 'Result',

            'deal': 'In deal',
            'cancel_deal': 'Cancel deal',
            'take': 'Take',
            'stop': 'Stop',
            'breakeven': 'Breakeven'
        },
        'uz': {
            'save': 'Hisobni saqlash',
            'del': 'O\'chirish',
            'change': 'O\'zgartirish',
            'img': 'Rasm va tavsif',
            'result': 'Natija',

            'deal': 'Sudada',
            'cancel_deal': 'Sudani bekor qilish',
            'take': 'Olish',
            'stop': 'Toʻxtatish',
            'breakeven': 'Tenglash'
        },
        'tr': {
            'save': 'Hesaplamayı kaydet',
            'del': 'Silmek',
            'change': 'Değiştir',
            'img': 'Resim ve açıklama',
            'result': 'Sonuç',

            'deal': 'Anlaşmada',
            'cancel_deal': 'Anlaşmayı iptal et',
            'take': 'Al',
            'stop': 'Durdur',
            'breakeven': 'Kâr-zarar noktası'
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    if isResult:
        if calc.status == 'WAIT' or calc.status == 'DEAL':
            if calc.status != 'DEAL':
                btn_deal = getButton(
                    texts[lang]['deal'], 'result_deal', stat_id=calc.id
                )
                btn_cancel = getButton(
                    texts[lang]['cancel_deal'], 'result_cancel', stat_id=calc.id
                )

                keyboard.add(
                    btn_cancel, btn_deal,
                )

            btn_take = getButton(
                texts[lang]['take'], 'result_take', stat_id=calc.id
            )
            btn_stop = getButton(
                texts[lang]['stop'], 'result_stop', stat_id=calc.id
            )
            keyboard.add(
                btn_stop, btn_take
            )
        keyboard.add(
            getChannelButton(
                texts[lang]['breakeven'],
                'take+0', calc.id, True
            ),
            getButton(back_txt(lang), 'back_calc', calc.id)
        )
    else:
        btn_delete = getButton(
            f'❌ {texts[lang]["del"]}',
            'delete_calc', calc.id
        )
        btn_change = getButton(
            f'✏️ {texts[lang]["change"]}',
            'ch_c', calc.id
        )
        btn_add_img = getButton(
            f'🖼 {texts[lang]["img"]}', 'add_img_text', calc.id
        )
        keyboard.add(btn_add_img)
        keyboard.add(btn_delete, btn_change)

        if not calc.inStat:
            keyboard.add(
                getButton(
                    '⚡️ ' + texts[lang]['result'],
                    'result_calc', calc.id
                )
            )
        if isAdmin and send_data is None:
            keyboard.add(
                getButton('Выложить в каналах', 'send_to_channels', calc.id)
            )

    return keyboard


def kb_freeze_calc(user_id: int):
    lang = get_lang(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)

    hours = {
        'ru': 'ч',
        'en': 'h',
        'uz': 'c',
        'tr': 's',
    }

    btn_3 = getButton(f'3 {hours[lang]}', 'time+3')
    btn_6 = getButton(f'6 {hours[lang]}', 'time+6')
    btn_9 = getButton(f'9 {hours[lang]}', 'time+9')
    btn_12 = getButton(f'12 {hours[lang]}', 'time+12')
    btn_back = getButton(cancel_txt(lang), 'go_main')

    keyboard.add(btn_3, btn_6)
    keyboard.add(btn_9, btn_12)
    keyboard.add(btn_back)

    return keyboard


def kb_deal_result(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'minus': 'Стоп-лосс',
            'sum': 'Иная сумма',
        },
        'en': {
            'minus': 'Stop loss',
            'sum': 'Other amount',
        },
        'uz': {
            'minus': 'Yo\'qotishni to\'xtating',
            'sum': 'Boshqa miqdor',
        },
        'tr': {
            'minus': 'Stop loss',
            'sum': 'Boshqa miqdor',
        },
    }

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    calc_info = calculation.get(stat_id)
    tp: list[int] = getattr(calc_info, 'tpRatio', [])

    buttons = []
    for i, el in enumerate(tp):
        btn = getButton(f'x{el}', f'profit+{el}', stat_id)
        buttons.append(btn)
        if len(buttons) == row_width or (i == len(tp) - 1 and len(buttons) != 0):
            keyboard.add(*buttons)
            buttons = []

    btn_low = getButton(f'{texts[lang]["minus"]}', 'profit+-', stat_id)
    btn_sum = getButton(f'{texts[lang]["sum"]}', 'sum', stat_id)
    btn_back = getButton(cancel_txt(lang), 'profit+cancel', stat_id)

    keyboard.add(btn_sum, btn_low, btn_back)

    return keyboard


def kb_deal_profit_minus(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup(row_width=3)

    btn_cancel = getButton(back_txt(lang), 'profit+cancel', stat_id)
    btn_x1 = getButton('x1', 'profit+loss1', stat_id)
    btn_x1_5 = getButton('x1.5', 'profit+loss1.5', stat_id)
    btn_x2 = getButton('x2', 'profit+loss2', stat_id)

    keyboard.add(btn_x1, btn_x1_5, btn_x2, btn_cancel)
    return keyboard


def kb_deal_profit_cancel(user_id: int, stat_id: int):
    lang = get_lang(user_id)
    btn_cancel = getButton(cancel_txt(lang), 'profit+cancel', stat_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_cancel)
    return keyboard


def kb_calculate_delete(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'yes': 'Да',
            'no': 'Нет',
        },
        'en': {
            'yes': 'Yes',
            'no': 'No',
        },
        'uz': {
            'yes': 'Ha',
            'no': 'Yo\'q',
        },
        'tr': {
            'yes': 'Evet',
            'no': 'HAYIR',
        },
    }

    btn_yes = getButton(f'✅ {texts[lang]["yes"]}', 'delete_calc_yes', stat_id)
    btn_no = getButton(f'❌ {texts[lang]["no"]}', 'delete_calc_no', stat_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_no, btn_yes)
    return keyboard


def kb_calculate_change(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'open_price': 'Цену входа',
            'stop_loss': 'Стоп-лосс',
            'tool': 'Инструмент',
            'style': 'Стиль',
        },
        'en': {
            'open_price': 'Open price',
            'stop_loss': 'Stop loss',
            'tool': 'Tool',
            'style': 'Style',
        },
        'uz': {
            'open_price': 'Ochiq narx',
            'stop_loss': 'Stop loss',
            'tool': 'Asbob',
            'style': 'Uslubi',
        },
        'tr': {
            'open_price': 'açılış fiyatını',
            'stop_loss': 'Stop loss',
            'tool': 'Enstrüman',
            'style': 'Tarzı',
        },
    }

    btn_op = getButton(texts[lang]["open_price"],
                       'ch_c+open_price', stat_id)
    btn_sl = getButton(texts[lang]["stop_loss"],
                       'ch_c+stop_loss', stat_id)
    btn_tool = getButton(texts[lang]["tool"], 'ch_c+tool', stat_id)
    btn_style = getButton(texts[lang]["style"], 'ch_c+style', stat_id)
    btn_back = getButton(back_txt(lang), 'ch_c+back', stat_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_op, btn_sl)
    keyboard.add(btn_tool, btn_style)
    keyboard.add(btn_back)
    return keyboard


def kb_calc_image_text(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    calc = calculation.get(stat_id)

    isReset = False
    if calc is not None and (calc.photo is not None or calc.description is not None):
        isReset = True

    texts = {
        'ru': {
            'reset': 'Убрать картинку и описание',
        },
        'en': {
            'reset': 'Remove picture and description',
        },
        'uz': {
            'reset': 'Rasm va tavsifni olib tashlash',
        },
        'tr': {
            'reset': 'Resim ve açıklamayı kaldır',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=1)

    if isReset:
        btn_reset = getButton(texts[lang]['reset'], 'remove_img_text', stat_id)
        keyboard.add(btn_reset)

    btn_back = getButton(back_txt(lang), 'back_calc', stat_id)
    keyboard.add(btn_back)

    return keyboard


def kb_confirm_channel_post(calc_id: int):
    send_data = channel_calc.getByCalc(calc_id)
    calc = calculation.get(calc_id)

    send = getButton('Отправить ➡️', f'stc+send', calc_id)
    rescreen = getButton('Повтор скрина', f'stc+rescreen', calc_id)

    is_text = is_photo = is_vote = without_stop = False
    if send_data is not None and calc is not None:
        is_text = calc.description is not None
        is_photo = calc.photo is not None
        without_stop = send_data.withoutStop
        is_vote = send_data.isVote

    if is_text:
        add_text = getButton('❌ Убрать описание', 'stc-text', calc_id)
    else:
        add_text = getButton('📝 Описание', 'stc+text', calc_id)

    if is_photo:
        add_photo = getButton('❌ Убрать скрин', 'stc-photo', calc_id)
    else:
        add_photo = getButton('🖼 Скрин', 'stc+photo', calc_id)

    if without_stop:
        add_stop = getButton('Вернуть стоп', 'stc+stop', calc_id)
    else:
        add_stop = getButton('Убрать стоп', 'stc+stop', calc_id)

    if is_vote:
        btn_vote = getButton('Убрать опрос', 'stc+vote', calc_id)
    else:
        btn_vote = getButton('Добавить опрос', 'stc+vote', calc_id)

    btn_style = getButton('Стиль', 'ch_c+style_stc', calc_id)
    add_time = getButton('Период', 'stc+time', calc_id)
    cancel = getButton(cancel_txt('ru'), 'go_main')

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        add_photo, add_text,  # rescreen,
        btn_vote, add_stop,
        add_time, btn_style,

        cancel, send,
    )
    return keyboard


def kb_channel_url(lang: LANGUAGES_TYPE, stat_id: int, bot_name: str):
    texts = {
        'ru': 'Рассчитать',
        'en': 'Calculate',
    }

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(
            texts[lang], url=f'https://t.me/{bot_name}?start=calc_{stat_id}'
        ),
    )
    return keyboard


def kb_send_calc_time(stat_id: int, is_first=False):
    first = 'f' if is_first else ''

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton('Среднесрочная', f'{first}stc+time=avg', stat_id),
        getButton('Внутридневная', f'{first}stc+time=day', stat_id),
        getButton('' if is_first else 'Убрать',
                  f'{first}stc+time=none', stat_id),
    )
    return keyboard


def kb_send_back(stat_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        getButton(cancel_txt(), 'stc+back', stat_id)
    )
    return keyboard
