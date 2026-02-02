from typing import Literal
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.channel_post import getButton as getChannelButton
from common.keyboard import back_txt, cancel_txt, not_specify_txt

from models import MARKETS_TYPE, Calculation, LANGUAGES_TYPE, CallbackQuery


stats_factory = CallbackData('type', 'stat_id', 'sm', 'p', prefix='stats')


class StatsCallbackFilter(AdvancedCustomFilter):
    key = 'stats'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


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


def kb_stats_page(lang: LANGUAGES_TYPE):
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
            'list_canceled': 'Canceled',
        },
        # cSpell:disable
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
        # cSpell:enable
    }

    keyboard.add(
        getButton(texts[lang]['list_deal'], 'list+deal'),
        getButton(texts[lang]['list_wait'], 'list+wait'),
        getButton(texts[lang]['list_done'], 'list+done'),
        getButton(texts[lang]['list_canceled'], 'list+canceled'),
        getButton(back_txt(lang), 'go_main'),
    )

    return keyboard


def kb_calc_list(lang: LANGUAGES_TYPE, page: int, count: int, list_type: str):
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


def kb_calc_result(lang: LANGUAGES_TYPE,
                   #    user_db_id: int,
                   calc: Calculation, isResult=False):
    # isAdmin = db.get_worker_role(user_db_id)
    isAdmin = False
    # send_data = channel_calc.getByCalc(calc.id)

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
            'wait': 'В ожидание',
            'take': 'Тейк',
            'stop': 'Стоп',
            'breakeven': 'Безубыток',

            'active': 'Активировать сделку',
            'refresh': 'Обновить',
            'active_p': 'Управление',
        },
        'en': {
            'save': 'Save to stats',
            'del': 'Delete',
            'change': 'Change',
            'img': 'Description',
            'comment': 'Comment',
            'result': 'Result',

            'calc_stats': 'Deals',

            'deal': 'In deal',
            'cancel_deal': 'Cancel deal',
            'wait': 'In wait',
            'take': 'Take',
            'stop': 'Stop',
            'breakeven': 'Breakeven',

            'active': 'Activate the deal',
            'refresh': 'Refresh',
            'active_p': 'Management',
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
            'wait': 'Kutish paytida',
            'take': 'Olish',
            'stop': 'Toʻxtatish',
            'breakeven': 'Tenglash',

            'active': 'Bitimni faollashtirish',
            'refresh': 'Yangilamoq',
            'active_p': 'Boshqaruv',
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
            'wait': 'Beklemede',
            'take': 'Al',
            'stop': 'Durdur',
            'breakeven': 'Kâr-zarar noktası',


            'active': 'Anlaşmayı etkinleştir',
            'refresh': 'Yenilemek',
            'active_p': 'Yönetim',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2 if isResult else 3)

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
            else:
                keyboard.add(getButton(
                    texts[lang]['wait'], 'result_wait', stat_id=calc.id
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

            # if send_data is not None:
            #     buttons.append(
            #         getButton(
            #             f'{texts[lang]["comment"]}',
            #             'comment', calc.id
            #         )
            #     )
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

        if not calc.ActiveCalc and (calc.status == 'WAIT' or calc.status == 'DEAL'):
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

        if isAdmin:
            keyboard.add(
                getButton('Выложить в каналах', 'send_to_channels', calc.id)
            )

        # if isActiveCalcSub and calc.ActiveCalc is None and calc.status == 'WAIT':
        #     keyboard.add(
        #         getButton(
        #             '⚡️ ' + texts[lang]['active'],
        #             'active_calc_a', calc.id
        #         )
        #     )
        # elif calc.ActiveCalc and (calc.status == 'WAIT' or calc.status == 'DEAL'):
        #     keyboard.add(
        #         getButton(
        #             '⚡️ ' + texts[lang]['active_p'],
        #             'active_calc', calc.id
        #         ),
        #         getButton(
        #             '🔄',
        #             'refresh', calc.id
        #         )
        #     )

    return keyboard


def kb_deal_result(lang: LANGUAGES_TYPE, stat_id: int):
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

    # TODO - calculation.get(userId=1, calcId=stat_id)
    calc_info = None
    tp: list[int] = getattr(calc_info, 'tpRatio', []) if calc_info else []

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


def kb_deal_profit_minus(lang: LANGUAGES_TYPE, stat_id: int):
    keyboard = InlineKeyboardMarkup(row_width=3)

    btn_cancel = getButton(back_txt(lang), 'profit+cancel', stat_id)
    btn_x1 = getButton('x1', 'profit+loss1', stat_id)
    btn_x1_5 = getButton('x1.5', 'profit+loss1.5', stat_id)
    btn_x2 = getButton('x2', 'profit+loss2', stat_id)

    keyboard.add(btn_x1, btn_x1_5, btn_x2, btn_cancel)
    return keyboard


def kb_deal_profit_cancel(lang: LANGUAGES_TYPE, stat_id: int):
    btn_cancel = getButton(cancel_txt(lang), 'profit+cancel', stat_id)

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(btn_cancel)
    return keyboard


def kb_calculate_delete(lang: LANGUAGES_TYPE, stat_id: int):
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


def kb_calculate_change(lang: LANGUAGES_TYPE, calc: Calculation):
    texts = {
        'ru': {
            'dep': 'Депозит',
            'risk': 'Риск',
            'open_price': 'Цену входа',
            'stop_loss': 'Стоп-лосс',
            'tool': 'Инструмент',
            'style': 'Стиль',
            'take_profit': 'Тейки',
        },
        'en': {
            'dep': 'Deposit',
            'risk': 'Risk',
            'open_price': 'Entry price',
            'stop_loss': 'Stop loss',
            'tool': 'Tool',
            'style': 'Style',
            'take_profit': 'Takes',
        },
        'uz': {
            'dep': 'Depozit',
            'risk': 'Xavf',
            'open_price': 'Ochiq narx',
            'stop_loss': 'Stop loss',
            'tool': 'Asbob',
            'style': 'Uslubi',
            'take_profit': 'Davom etadi',
        },
        'tr': {
            'dep': 'Depozito',
            'risk': 'Risk',
            'open_price': 'açılış fiyatını',
            'stop_loss': 'Stop loss',
            'tool': 'Enstrüman',
            'style': 'Tarzı',
            'take_profit': 'Almak',
        },
    }

    btn_op = getButton(
        texts[lang]["open_price"],
        'ch_c+open_price', calc.id
    )
    btn_sl = getButton(
        texts[lang]["stop_loss"],
        'ch_c+stop_loss', calc.id
    )
    btn_tool = getButton(texts[lang]["tool"], 'ch_c+tool', calc.id)
    btn_style = getButton(texts[lang]["style"], 'ch_c+style', calc.id)
    btn_take_profit = getButton(
        texts[lang]["take_profit"], 'ch_c+take', calc.id
    )
    btn_back = getButton(back_txt(lang), 'ch_c+back', calc.id)

    keyboard = InlineKeyboardMarkup(row_width=2)

    if calc.status != 'FINISH':
        keyboard.add(
            getButton(
                texts[lang]['dep'], 'ch_c+dep', calc.id
            ),
            getButton(
                texts[lang]['risk'], 'ch_c+risk', calc.id
            ),
        )

    if not calc.ActiveCalc:
        keyboard.add(btn_op, btn_sl)
        keyboard.add(btn_tool, btn_style)
        keyboard.add(btn_take_profit, btn_back)
    else:
        keyboard.add(btn_style)
        keyboard.add(btn_back)

    return keyboard


def kb_calc_image_text(lang: LANGUAGES_TYPE, calc: Calculation, type: Literal['stc+', ''] = ''):
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
        btn_reset = getButton(
            texts[lang]['reset'],
            f'{type}del_img_txt', calc.id
        )
        keyboard.add(btn_reset)

    btn_back = getButton(
        back_txt(lang),
        'stc+back' if type == 'stc+' else 'back_calc',
        calc.id
    )
    keyboard.add(btn_back)

    return keyboard


def kb_confirm_channel_post(calc_id: int):
    # TODO - Получение инфо о данных по каналу
    send_data = None
    # TODO - calculation.get(userId=1, calcId=calc_id)
    calc = None

    send = getButton('Отправить ➡️', f'stc+send', calc_id)

    is_vote = without_stop = False
    if send_data is not None and calc is not None:
        without_stop = send_data.withoutStop
        is_vote = send_data.isVote

    add_description = getButton('🖼 Описание', 'stc+add_img_text', calc_id)

    if without_stop:
        add_stop = getButton('Выводить стоп', 'stc+stop', calc_id)
    else:
        add_stop = getButton('Не выводить стоп', 'stc+stop', calc_id)

    if is_vote:
        btn_vote = getButton('Убрать опрос', 'stc+vote', calc_id)
    else:
        btn_vote = getButton('Добавить опрос', 'stc+vote', calc_id)

    btn_style = getButton('Стиль', 'ch_c+style_stc', calc_id)
    add_time = getButton('Период', 'stc+time', calc_id)

    takes = getButton('Тейки', 'auto_take', calc_id)
    tr_stop = getButton('Скользящий стоп', 'ch_tr_stop', calc_id)

    cancel_at = getButton(
        'Время отмены', 'stc_cancel_at', calc_id
    )

    cancel = getButton(cancel_txt('ru'), 'go_main')

    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        add_description, btn_vote,
        add_time, btn_style,
    )
    keyboard.add(
        add_stop, takes,
        tr_stop, cancel_at,
    )
    keyboard.add(
        cancel, send,
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


def kb_cancel_at(lang: LANGUAGES_TYPE, calc_id: int, action: Literal['stc_', ''] = ''):
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        getButton('1h', f'{action}cancel_at+1h', calc_id),
        getButton('4h', f'{action}cancel_at+4h', calc_id),
        getButton('1d', f'{action}cancel_at+1d', calc_id),
    )
    keyboard.add(
        getButton(not_specify_txt(lang), f'{action}cancel_at+0', calc_id),
        getButton(
            back_txt(lang),
            'stc+back' if action == 'stc_' else 'active_calc',
            calc_id
        )
    )
    return keyboard


def kb_channel_trailing_stop(lang: LANGUAGES_TYPE, calc_id: int, is_channel=False):
    is_channel = 'ch_' if is_channel else ''

    keyboard = InlineKeyboardMarkup(row_width=4)

    buttons = []
    for i in range(1, 5):
        buttons.append(
            getButton(f'{i}', f'{is_channel}tr_stop+{i}', calc_id)
        )

    keyboard.add(*buttons)
    keyboard.add(
        getButton(not_specify_txt(lang), f'{is_channel}tr_stop+0', calc_id),
        getButton(back_txt(lang), 'active_calc', calc_id),
    )
    return keyboard


def kb_calc_activation(lang: LANGUAGES_TYPE, calc: Calculation):
    texts = {
        'ru': {
            'cancelAt': 'Время отмены',
            'tr_stop': 'Скользящий стоп',
            'new_stop': 'Сдвинуть стоп',
            'auto_take': 'Тейк',
            'cancel': 'Отменить сделку',
            'profit': 'Закрыть сделку',
        },
        'en': {
            'cancelAt': 'Cancel at',
            'tr_stop': 'Trailing stop',
            'new_stop': 'Move the stop',
            'auto_take': 'Take',
            'cancel': 'Cancel the deal',
            'profit': 'Close the deal ',
        },
        'uz': {
            'cancelAt': 'Bekor qilish vaqti',
            'tr_stop': 'Slip stop',
            'new_stop': 'To\'xtashni harakatga keltiring',
            'auto_take': 'Take',
            'cancel': 'Bitimni bekor qiling',
            'profit': 'Bitimni yoping',
        },
        'tr': {
            'cancelAt': 'Iptal etmek',
            'tr_stop': 'Kayan durdurma',
            'new_stop': 'Durumu hareket et',
            'auto_take': 'Take',
            'cancel': 'Anlaşmayı iptal et',
            'profit': 'Anlaşmayı kapat ',
        },
    }

    keyboard = InlineKeyboardMarkup(row_width=2)

    buttons = []

    if calc.status == 'WAIT':
        buttons.append(
            getButton(
                texts[lang]['cancelAt'], 'cancel_at', calc.id
            ),
        )

    buttons.append(
        getButton(
            texts[lang]['auto_take'],
            'auto_take', calc.id
        ),
    )

    keyboard.add(*buttons)
    buttons = []

    keyboard.add(
        getButton(
            texts[lang]['tr_stop'], 'tr_stop', calc.id
        ),
        getButton(
            texts[lang]['new_stop'], 'new_stop', calc.id
        ),
    )

    if calc.status == 'WAIT':
        buttons.append(
            getButton(
                texts[lang]['cancel'], 'cancel', calc.id
            ),
        )
    elif calc.status == 'DEAL':
        buttons.append(
            getChannelButton(
                texts[lang]['profit'], 'result_end', calc.id
            ),
        )

    keyboard.add(*buttons)
    buttons = []

    keyboard.add(
        getButton(
            back_txt(lang), 'back_calc', calc.id
        ),
    )

    return keyboard


def kb_auto_take(lang: LANGUAGES_TYPE, calc_id: int):
    keyboard = InlineKeyboardMarkup(row_width=5)

    buttons = []
    for i in range(1, 11):
        buttons.append(
            getButton(f'{i}', f'kb_auto_take+{i}', calc_id)
        )

    keyboard.add(*buttons)
    keyboard.add(
        getButton('Указать свою цену', 'take_price', calc_id)
    )
    keyboard.add(
        getButton(not_specify_txt(lang), 'auto_take+null', calc_id),
        getButton(
            back_txt(lang),
            'active_calc', calc_id
        )
    )
    return keyboard


def kb_confirm_take_price(lang: LANGUAGES_TYPE, calc_id: int):
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

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        getButton(texts[lang]['no'], 'take_price', calc_id),
        getButton(texts[lang]['yes'], 'take_price_yes', calc_id),
    )
    return keyboard


def kb_calc_back(lang: LANGUAGES_TYPE, calc_id: int):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        getButton(back_txt(lang), 'active_calc', calc_id)
    )
    return keyboard


def kb_channel_item_back(calc_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        getButton(back_txt('ru'), 'channel_item', calc_id)
    )
    return keyboard


def kb_channel_confirm_back(calc_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        getButton(back_txt('ru'), 'stc+back', calc_id)
    )
    return keyboard
