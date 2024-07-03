from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboard import cancel_txt
from common.utils import get_lang
from models import Calculation

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


def kb_main(user_id: int, is_access=True, stat: Calculation | None = None, is_unfinished=False, is_try=False):
    lang = get_lang(user_id)
    texts = {
        'ru': {
            'calc': 'Сделать расчёт' if not is_try else 'Новый расчёт',
            'calc_continue': 'Продолжить расчёт',
            'settings': 'Настройки',
            'buy': 'Купить',
            'stats': 'Ваша статистика',
            'link': 'Обновления',
        },
        'en': {
            'calc': 'Make a calculation' if not is_try else 'New calculation',
            'calc_continue': 'Сontinue calculation',
            'settings': 'Settings',
            'buy': 'Buy',
            'stats': 'Your stats',
            'link': 'Updates',
        },
        'uz': {
            'calc': 'Hisoblash',
            'calc_continue': 'Hisoblashni davom eting',
            'settings': 'Sozlamalar',
            'buy': 'Sotib olish',
            'stats': 'Sizning stastitikangiz',
            'link': 'Yangilanishlar',
        },
        'tr': {
            'calc': 'Hesaplama',
            'calc_continue': 'Hesaplamaya devam et',
            'settings': 'Ayarlar',
            'buy': 'Satın al',
            'stats': 'Sizin istatistik',
            'link': 'Yenilemeler',
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

    btn_settings = getButton(
        '⚙️ ' + texts[lang]['settings'], 'settings', saved, stat_id=stat_id
    )
    buttons.append(btn_settings)


    if not is_try:
        if stat is None:
            btn_buy = getButton(f"💰 {texts[lang]['buy']}", 'buy')
            btn_stats = getButton('📊 ' + texts[lang]['stats'], 'stats')

            link = 'profmarkets' if lang == 'ru' else 'promarketsen'
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


def kb_after_first_settings(user_id: int):
    lang = get_lang(user_id)

    texts = {
        'ru': {
            'calc': 'Сделать первый расчет',
        },
        'en': {
            'calc': 'Make a first calculation',
        },
        'uz': {
            'calc': 'Birinchi hisoblashni amalga oshiring',
        },
        'tr': {
            'calc': 'İlk hesaplamayı yap',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton('⌨️ ' + texts[lang]['calc'], 'first_try'),
    )
    return keyboard