from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.stats import kb_calc_result

from common.keyboard import back_txt
from models import LANGUAGES_TYPE, Calculation, CallbackQuery


main_factory = CallbackData('type', 'stat_id', 'is_saved', prefix='main')


class MainCallbackFilter(AdvancedCustomFilter):
    key = 'main'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str, is_saved=False, stat_id=-1):
    return InlineKeyboardButton(
        text, None,
        main_factory.new(
            type=type,
            stat_id=str(stat_id),
            is_saved=str(is_saved)
        )
    )


def kb_main(lang: LANGUAGES_TYPE, user_id: int, is_access=True, stat: Calculation | None = None, is_unfinished=False, is_first=False):
    # TODO
    # user_db_id = db.get_user_id_by_tg_id(user_id)
    # isAdmin = db.get_worker_role(user_db_id)
    isAdmin = False

    texts = {
        'ru': {
            'calc': 'Сделать расчёт',
            'calc_continue': 'Продолжить расчёт',
            'settings': 'Настройки',
            'buy': 'Купить',
            'stats': 'Ваша статистика',
            'link': 'Сигналы',
            'info': 'Инструкция',
            'violations': 'Нарушения',
            'active': 'Активные сделки',
        },
        'en': {
            'calc': 'Make a calculation',
            'calc_continue': 'Сontinue calculation',
            'settings': 'Settings',
            'buy': 'Buy',
            'stats': 'Your stats',
            'link': 'Signals',
            'info': 'Manual',
            'violations': 'Violations',
            'active': 'Active calcs',
        },
        'uz': {
            'calc': 'Hisoblash',
            'calc_continue': 'Hisoblashni davom eting',
            'settings': 'Sozlamalar',
            'buy': 'Sotib olish',
            'stats': 'Sizning stastitikangiz',
            'link': 'Signallar',
            'info': 'Qo\'llanma',
            'violations': 'Buzish',
            'active': 'Faol bitimlar',
        },
        'tr': {
            'calc': 'Hesaplama',
            'calc_continue': 'Hesaplamaya devam et',
            'settings': 'Ayarlar',
            'buy': 'Satın al',
            'stats': 'Sizin istatistik',
            'link': 'Sinyaller',
            'info': 'Manuel',
            'violations': 'İhlaller',
            'active': 'Aktif fırsatlar',
        },
    }

    stat_id = -1
    saved = False
    if stat is not None:
        stat_id = stat.id or stat_id
        saved = stat.status == 'FINISH'

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
            'calc', saved, stat_id if not is_first else -111,
        )
        buttons.append(btn_calc)

    # if isAdmin:
        # buttons.append(
        #     getButton('Расчёт для канала', 'ch_calc', saved, stat_id)
        # )

    btn_settings = getButton(
        '⚙️ ' + texts[lang]['settings'], 'settings', saved, stat_id
    )
    buttons.append(btn_settings)

    if not is_first:
        if stat is None:
            btn_stats = getButton(
                '📊 ' + texts[lang]['stats'], 'stats', saved, stat_id
            )
            buttons.append(btn_stats)

            link = 'my_investors' if lang == 'ru' else '+386iRxc4XKszMDIy'
            btn_link = InlineKeyboardButton(
                texts[lang]['link'], f'https://t.me/{link}'
            )

            btn_info = getButton(texts[lang]['info'], 'info')

            buttons.append(btn_link)
            buttons.append(btn_info)

            buttons.append(
                getButton(texts[lang]['violations'], 'violations')
            )

            keyboard.add(*buttons)
            buttons = []

            if isAdmin:
                btn_stats = getButton('Расчёты канaла', 'channels')
                buttons.append(btn_stats)
        else:
            kb = kb_calc_result(lang, stat)
            buttons_rows = kb.keyboard

            for row in buttons_rows:
                keyboard.add(
                    *row,
                    row_width=kb.row_width
                )

    keyboard.add(*buttons)
    return keyboard


def kb_first_calc(lang: LANGUAGES_TYPE):
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


def kb_violation(lang: LANGUAGES_TYPE, isToday: bool, canEdit: bool, is_edit: bool):
    keyboard = InlineKeyboardMarkup(row_width=3)

    texts = {
        'ru': {
            'yes': 'Нарушил',
            'no': 'Не нарушил',
            'none': 'Не торговал',
            'edit': 'Изменить',
        },
        'en': {
            'yes': 'Violated',
            'no': 'Not violated',
            'none': 'Not traded',
            'edit': 'Edit',
        },
        'uz': {
            'yes': 'Buzilgan',
            'no': 'Buzilmagan',
            'none': 'Sotilmaydi',
            'edit': 'O\'zgarish',
        },
        'tr': {
            'yes': 'Yozlaşmış',
            'no': 'Kırılmamış',
            'none': 'Takas edilmemiştir',
            'edit': 'Değiştirmek',
        }
    }

    if not isToday or is_edit:
        edit = '_edit' if is_edit else ''
        keyboard.add(
            getButton(texts[lang]['yes'], f'violation{edit}+yes'),
            getButton(texts[lang]['no'], f'violation{edit}+no'),
            getButton(texts[lang]['none'], f'violation{edit}+null'),
        )
    elif canEdit:
        keyboard.add(
            getButton(texts[lang]['edit'], 'violation_edit'),
        )

    keyboard.add(
        getButton(back_txt(lang), 'go_main' if not is_edit else 'violations')
    )
    return keyboard


def kb_violation_skip(lang: LANGUAGES_TYPE):
    keyboard = InlineKeyboardMarkup(row_width=2)

    texts = {
        'ru': 'Пропустить',
        'en': 'Skip',
        'uz': 'O\'tkazib yubormoq',
        'tr': 'Atlamak',
    }

    keyboard.add(
        getButton(texts[lang], 'violations'),
    )
    return keyboard
