from typing import Literal
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from CALCULATE.common.messages import market_translates
from common.keyboard import back_txt, cancel_txt
from common.utils import get_lang

from db import LANGUAGES_TYPE, db
from models import MARKETS_TYPE
from services import calculation, channel_calc

from .filter import stats_factory


def getButton(text: str, type: str, stat_id=0, stats_market: MARKETS_TYPE = 'crypto'):
    return InlineKeyboardButton(
        text, None,
        stats_factory.new(
            type=type,
            stat_id=stat_id,
            stats_market=stats_market,
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


def kb_calc_result(user_id: int, stat_id: int, is_saved=False):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    isAdmin = db.get_worker_role(user_db_id)
    send_data = channel_calc.getByCalc(stat_id)

    texts = {
        'ru': {
            'save': 'Сохранить в статистику',
            'del': 'Удалить',
            'change': 'Изменить',
            'img': 'Прикрепить фото',
        },
        'en': {
            'save': 'Save to stats',
            'del': 'Delete',
            'change': 'Change',
            'img': 'Attach image',
        },
        'uz': {
            'save': 'Hisobni saqlash',
            'del': 'O\'chirish',
            'change': 'O\'zgartirish',
            'img': 'Rasmni qo\'shish',
        },
        'tr': {
            'save': 'Hesaplamayı kaydet',
            'del': 'Silmek',
            'change': 'Değiştir',
            'img': 'Resim ekle',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_delete = getButton(
        f'❌ {texts[lang]["del"]}',
        'delete_calc', stat_id
    )
    btn_change = getButton(
        f'✏️ {texts[lang]["change"]}',
        'ch_c', stat_id
    )
    keyboard.add(btn_delete, btn_change)

    if is_saved:
        if not isAdmin:
            btn_add_img = getButton(f'🖼 {texts[lang]["img"]}', 'add_img', stat_id)
            keyboard.add(btn_add_img)
    else:
        if isAdmin:
            if send_data is not None and (send_data.status == 'WAIT' or send_data.status == 'DEAL'):
                if send_data.status != 'DEAL':
                    btn_deal = getButton(
                        'В сделке', 'result_deal', stat_id=stat_id
                    )
                    btn_cancel = getButton(
                        'Отмена сделки', 'result_cancel', stat_id=stat_id
                    )
                    keyboard.add(
                        btn_cancel, btn_deal,
                    )

                btn_take = getButton('Тейк', 'result_take', stat_id=stat_id)
                btn_stop = getButton('Стоп', 'result_stop', stat_id=stat_id)
                keyboard.add(
                    btn_stop, btn_take
                )
        else:
            btn_save = getButton(
                f'✅ {texts[lang]["save"]}', 'profit+', stat_id
            )
            keyboard.add(btn_save)

    if isAdmin and send_data is None:
        keyboard.add(
            getButton('Выложить в каналах', 'send_to_channels', stat_id)
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
    tp: list[int] = getattr(calc_info, 'tp_ratio', [])

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


def kb_calc_image(user_id: int, stat_id: int):
    lang = get_lang(user_id)

    btn_back = getButton(back_txt(lang), 'profit+cancel', stat_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_back)
    return keyboard


def kb_confirm_channel_post(stat_id: int):
    send_data = channel_calc.getByCalc(stat_id)

    send = getButton('Отправить ➡️', f'stc+send', stat_id)
    rescreen = getButton('Повтор скрина', f'stc+rescreen', stat_id)

    is_text = is_photo = is_vote = without_stop = False
    if send_data is not None:
        is_text = send_data.text is not None
        is_photo = send_data.photo is not None
        without_stop = send_data.withoutStop
        is_vote = send_data.isVote

    if is_text:
        add_text = getButton('❌ Убрать описание', 'stc-text', stat_id)
    else:
        add_text = getButton('📝 Описание', 'stc+text', stat_id)

    if is_photo:
        add_photo = getButton('❌ Убрать скрин', 'stc-photo', stat_id)
    else:
        add_photo = getButton('🖼 Скрин', 'stc+photo', stat_id)

    if without_stop:
        add_stop = getButton('Вернуть стоп', 'stc+stop', stat_id)
    else:
        add_stop = getButton('Убрать стоп', 'stc+stop', stat_id)

    if is_vote:
        btn_vote = getButton('Убрать опрос', 'stc+vote', stat_id)
    else:
        btn_vote = getButton('Добавить опрос', 'stc+vote', stat_id)

    btn_style = getButton('Стиль', 'ch_c+style_stc', stat_id)
    add_time = getButton('Период', 'stc+time', stat_id)
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
