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
