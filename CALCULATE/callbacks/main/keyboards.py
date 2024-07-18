from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import cancel_txt
from common.utils import get_lang
from models import Calculation
from db import db

from ..stats.keyboards import kb_calc_result
from .filter import main_factory


def getButton(text: str, type: str, is_saved=False, stat_id=-1):
    return InlineKeyboardButton(
        text, None,
        main_factory.new(
            type=type,
            stat_id=str(stat_id),
            is_saved=str(is_saved)
        )
    )


def cancel_btn(user_id: int):
    lang = get_lang(user_id)

    return getButton(cancel_txt(lang), 'go_main')


def kb_main(user_id: int, is_access=True, stat: Calculation | None = None, is_unfinished=False, is_first=False):
    lang = get_lang(user_id)

    user_db_id = db.get_user_id_by_tg_id(user_id)
    isAdmin = db.get_worker_role(user_db_id)

    texts = {
        'ru': {
            'calc': 'Сделать расчёт',
            'calc_continue': 'Продолжить расчёт',
            'settings': 'Настройки',
            'buy': 'Купить',
            'stats': 'Ваша статистика',
            'link': 'Сигналы',
        },
        'en': {
            'calc': 'Make a calculation',
            'calc_continue': 'Сontinue calculation',
            'settings': 'Settings',
            'buy': 'Buy',
            'stats': 'Your stats',
            'link': 'Signals',
        },
        'uz': {
            'calc': 'Hisoblash',
            'calc_continue': 'Hisoblashni davom eting',
            'settings': 'Sozlamalar',
            'buy': 'Sotib olish',
            'stats': 'Sizning stastitikangiz',
            'link': 'Signallar',
        },
        'tr': {
            'calc': 'Hesaplama',
            'calc_continue': 'Hesaplamaya devam et',
            'settings': 'Ayarlar',
            'buy': 'Satın al',
            'stats': 'Sizin istatistik',
            'link': 'Sinyaller',
        },
    }

    stat_id = -1
    saved = False
    if stat is not None:
        stat_id = stat.id or stat_id
        saved = stat.in_stat

    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []

    if is_access:
        if is_unfinished:
            btn_continue_calc = getButton(
                '➡️ ' + texts[lang]['calc_continue'],
                'calc_continue', saved, stat_id
            )
            buttons.append(btn_continue_calc)
        btn_calc = getButton(
            '⌨️ ' + texts[lang]['calc'],
            'calc', saved, stat_id,
        )
        buttons.append(btn_calc)

    if isAdmin:
        buttons.append(
            getButton('Расчёт для канала', 'ch_calc', saved, stat_id)
        )
        # buttons.append(
        #     getButton('Обновить недельюную статистику', 'week_stat', saved, stat_id)
        # )

    btn_settings = getButton(
        '⚙️ ' + texts[lang]['settings'], 'settings', saved, stat_id=stat_id
    )
    buttons.append(btn_settings)


    if not is_first:
        if stat is None:
            btn_buy = getButton(f"💰 {texts[lang]['buy']}", 'buy')
            btn_stats = getButton('📊 ' + texts[lang]['stats'], 'stats')

            link = 'my_investors' if lang == 'ru' else '+386iRxc4XKszMDIy'
            btn_link = InlineKeyboardButton(texts[lang]['link'], f'https://t.me/{link}')

            buttons.append(btn_stats)
            buttons.append(btn_link)
            # buttons.append(btn_buy)
        else:
            kb = kb_calc_result(user_id, stat_id, saved)
            buttons_rows = kb.keyboard

            for row in buttons_rows:
                keyboard.add(*row, row_width=kb.row_width)

    keyboard.add(*buttons)
    return keyboard


def kb_first_calc(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'calc': 'Рассчитать',
        },
        'en': {
            'calc': 'Calculate',
        },
        'uz': {
            'calc': 'Hisoblamoq',
        },
        'tr': {
            'calc': 'Hesaplamak',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton('⌨️ ' + texts[lang]['calc'] + '!', 'first_try'),
    )
    return keyboard