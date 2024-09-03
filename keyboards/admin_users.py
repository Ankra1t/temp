from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.asyncio_filters import AdvancedCustomFilter

from common.keyboard import back_txt

from models import CallbackQuery


admin_users_factory = CallbackData(
    'type', 'sort_by', 'client_db_id', 'page', 'filter', prefix='admin_users'
)


class AdminUsersCallbackFilter(AdvancedCustomFilter):
    key = 'admin_users'

    async def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(call)


def getButton(text: str, type: str, sort_by='', page=1, client_db_id=0, filter=''):
    return InlineKeyboardButton(text, None, admin_users_factory.new(
        type=type,
        sort_by=sort_by,
        client_db_id=client_db_id,
        page=page,
        filter=filter
    ))


def kb_admin_users():
    keyboard = InlineKeyboardMarkup(row_width=2)

    lists = getButton('📋 Списки', 'lists')
    search = getButton('🔎 Поиск клиента', 'client_search')
    clients = getButton('👨‍💻 Все клиенты', 'client_list', 'new', 1)
    markets = getButton('По рынкам', 'markets')
    main = getButton(back_txt(), 'go_main')

    keyboard.add(clients, lists)
    keyboard.add(search, markets)
    keyboard.add(main)
    return keyboard


def kb_admin_choose_list():
    def getThisButton(text: str, filter: str):
        return getButton(text, 'client_list', '', 1, 0, filter)

    keyboard = InlineKeyboardMarkup(row_width=2)

    ban = getThisButton('⛔️ Бан', 'ban')
    # paid = getThisButton('💵 Платные', 'paid')
    new = getThisButton('🆕 Новые', 'new')
    back = getButton(back_txt(), 'go_users')

    keyboard.add(ban, new)
    keyboard.add(back)
    return keyboard


def kb_admin_client_list(pages: int, page: int, sort_by='', filter='', type='client_list'):
    def getThisButton(text: str, new_page: int, new_sort_by: str | None = None):
        new_sort_by = new_sort_by or sort_by
        return getButton(text, type, new_sort_by, new_page, 0, filter)

    row_width = 3
    keyboard = InlineKeyboardMarkup(row_width=row_width)

    btn_start = getThisButton('В начало', 1)
    btn_end = getThisButton('В конец', pages)
    btn_next = getThisButton('Далее', page + 1)
    btn_back = getThisButton('Назад', page - 1)

    counter = getButton(f'{page}/{pages}', 'counter')

    if pages > 1:
        if page == 1:
            keyboard.add(btn_end, counter, btn_next)
        elif page == pages:
            keyboard.add(btn_back, counter, btn_start)
        else:
            keyboard.add(btn_back, counter, btn_next)

        if sort_by == 'new':
            filter_text = 'Сортировать по старым'
            new_filter = 'old'
        else:
            filter_text = 'Сортировать по новым'
            new_filter = 'new'
        btn_filter = getThisButton(filter_text, 1, new_filter)
        keyboard.add(btn_filter)

    search = getButton('🔎 Поиск', 'client_search', sort_by, page)
    back = getButton(back_txt(), 'go_users')

    keyboard.add(search, back)
    return keyboard


def kb_admin_client_info(client_db_id: int, is_banned: bool, page=1, sort_by=''):
    def getClientButton(text: str, type: str):
        return getButton(text, type, '', 1, client_db_id)

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_ban = getClientButton(
        '✅ Разбанить' if is_banned else '🚫 Забанить', 'client_ban'
    )
    btn_remove_sub = getClientButton(
        '➖ Отменить подписку', 'client_cancel_sub'
    )
    btn_add_sub = getClientButton(
        '➕ Выдать подписку', 'client_add_sub'
    )
    btn_add_trial_sub = getClientButton(
        '🎁 Выдать пробный доступ', 'client_set_trial_custom'
    )

    # if sort_by != '' or page != 1:
    #     btn_client_list = getButton(
    #         '👨‍💻 Список клиентов', 'client_list', sort_by, page
    #     )
    # else:
    #     btn_client_list = kb_inl_admin.go_users_btn
    back = getButton(back_txt(), 'go_users')

    keyboard.add(btn_add_sub, btn_remove_sub)
    keyboard.add(btn_add_trial_sub)
    keyboard.add(btn_ban, back)
    return keyboard


def kb_admin_users_cancel(sort_by='', page=1, filter=''):
    keyboard = InlineKeyboardMarkup(row_width=2)

    # if sort_by != '' or page != 1:
    #     btn_cancel = getButton(
    #         '👨‍💻 Список клиентов', 'client_list', sort_by, page
    #     )
    # else:
    #     btn_cancel = kb_inl_admin.go_users_btn
    if filter != '':
        btn_cancel = getButton(back_txt(), 'lists')
    else:
        btn_cancel = getButton(back_txt(), 'go_users')

    keyboard.add(btn_cancel)
    return keyboard


def kb_admin_users_confirm(type_info: str, client_db_id: int):
    def getConfimButton(text: str, type: str):
        return getButton(text, f'confirm_{type}_{type_info}', '', 1, client_db_id)

    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_yes = getConfimButton('✅ Да', 'yes')
    btn_no = getConfimButton('❌ Нет', 'no')

    keyboard.add(btn_yes, btn_no)
    return keyboard


def kb_admin_choose_periods():
    keyboard = InlineKeyboardMarkup(row_width=2)

    week = getButton('Неделя', 'choose_periods_for_tariffs', sort_by='week')
    week2 = getButton(
        '2 Недели', 'choose_periods_for_tariffs', sort_by='week2')
    month = getButton('Месяц', 'choose_periods_for_tariffs', sort_by='month')
    month6 = getButton('6 мес', 'choose_periods_for_tariffs', sort_by='month6')
    year = getButton('Год', 'choose_periods_for_tariffs', sort_by='year')
    lifetime = getButton(
        'Пожизненно', 'choose_periods_for_tariffs', sort_by='lifetime')
    back = getButton(back_txt(), 'go_users')

    keyboard.add(week, week2)
    keyboard.add(month, month6)
    keyboard.add(year, lifetime)
    keyboard.add(back)
    return keyboard


def kb_admin_users_back():
    keyboard = InlineKeyboardMarkup(row_width=2)

    back = getButton(back_txt(), 'go_users')
    keyboard.add(back)

    return keyboard


def kb_admin_users_markets():
    keyboard = InlineKeyboardMarkup(row_width=2)

    btn_crypto = getButton('Крипта', 'markets', 'new', 1, 0, 'crypto')
    btn_forex = getButton('Форекс', 'markets', 'new', 1, 0, 'forex')
    btn_RF = getButton('РФ', 'markets', 'new', 1, 0, 'RF')
    btn_USA = getButton('США', 'markets', 'new', 1, 0, 'USA')
    btn_back = getButton(back_txt(), 'go_users')

    keyboard.add(btn_crypto, btn_forex, btn_RF, btn_USA, btn_back)
    return keyboard
