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
            'list_wait': 'В ожидании',
            'list_deal': 'В сделке',
            'list_done': 'Завершенные',
            'list_canceled': 'Отмененные',
        },
        'en': {
            'list_wait': 'In wait',
            'list_deal': 'In deal',
            'list_done': 'Completed',
            'list_canceled': 'Сanceled',
        },
        'uz': {
            'list_wait': 'Kutish jarayonida',
            'list_deal': 'Bitimda',
            'list_done': 'Tugallangan',
            'list_canceled': 'Bekor qilindi',
        },
        'tr': {
            'list_wait': 'Askıda olması',
            'list_deal': 'Anlaşmada',
            'list_done': 'Tamamlanmış',
            'list_canceled': 'İptal edildi',
        },
    }

    keyboard.add(
        getButton(texts[lang]['list_deal'], 'list+deal'),
        getButton(texts[lang]['list_wait'], 'list+wait'),
        getButton(texts[lang]['list_done'], 'list+done'),
        getButton(texts[lang]['list_canceled'], 'list+canceled'),
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
            'img': 'Описание',
            'comment': 'Комментарий',
            'result': 'Результат',

            'calc_stats': 'Сделки',

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
            'img': 'Description',
            'comment': 'Сomment',
            'result': 'Result',

            'calc_stats': 'Deals',

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
            'img': 'Tavsif',
            'comment': 'Sanktsiya',
            'result': 'Natija',

            'calc_stats': 'Bitimlar',

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
            'img': 'Açıklama',
            'comment': 'Comment',
            'result': 'Sonuç',

            'calc_stats': 'Fırsatlar',

            'deal': 'Anlaşmada',
            'cancel_deal': 'Anlaşmayı iptal et',
            'take': 'Al',
            'stop': 'Durdur',
            'breakeven': 'Kâr-zarar noktası'
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=3)

    if isResult:
        buttons = []
        if calc.status == 'WAIT' or calc.status == 'DEAL':
            if calc.status != 'DEAL':
                buttons.append(getButton(
                    texts[lang]['cancel_deal'], 'result_cancel', stat_id=calc.id
                ))
                buttons.append(getButton(
                    texts[lang]['deal'], 'result_deal', stat_id=calc.id
                ))

            buttons.append(getButton(
                texts[lang]['stop'], 'result_stop', stat_id=calc.id
            ))
            buttons.append(getButton(
                texts[lang]['take'], 'result_take', stat_id=calc.id
            ))
            buttons.append(
                getChannelButton(
                    texts[lang]['breakeven'],
                    'take+0', calc.id, True
                )
            )
        buttons.append(getButton(back_txt(lang), 'back_calc', calc.id))
        keyboard.add(*buttons)
    else:
        buttons = []

        if not (calc.status == 'FINISH' and calc.comment is not None):
            buttons.append(
                getButton(
                    f'🖼 {texts[lang]["img" if calc.status != "FINISH" else "comment"]}',
                    'add_img_text', calc.id
                )
            )

        if calc.status == 'WAIT' or calc.status == 'DEAL':
            buttons.append(
                getButton(
                    '⚡️ ' + texts[lang]['result'],
                    'result_calc', calc.id
                )
            )

        keyboard.add(*buttons)
        buttons = []

        buttons.append(getButton(
            f'❌',
            'delete_calc', calc.id
        ))
        buttons.append(getButton(
            f'✏️',
            'ch_c', calc.id
        ))
        buttons.append(getButton(
            '📊 ' + texts[lang]['calc_stats'],
            'go_stats', calc.id
        ))

        keyboard.add(*buttons)

        if calc.openedList:
            buttons.append(
                getButton(
                    '', ''
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


def kb_calc_image_text(user_id: int, calc: Calculation):
    lang = get_lang(user_id)

    isReset = False
    if calc.status != 'FINISH' and (calc.photo is not None or calc.description is not None):
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
        btn_reset = getButton(texts[lang]['reset'], 'remove_img_text', calc.id)
        keyboard.add(btn_reset)

    btn_back = getButton(back_txt(lang), 'back_calc', calc.id)
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
