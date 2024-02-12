from datetime import datetime
from gettext import find
from telebot import TeleBot
from telebot.types import Message

from initialize import logger

from common.utils import digit_accept, text_accept, set_state_data
from common.vars import DATE_FORMAT, PRINT_DATE_FROMAT

from initialize import base_statis


from MAIN.states import AdminStatisticsState
from MAIN.callbacks import kb_statistics_back



from db_new import db_new
# from initialize import kb_inl_admin, tariff_manager
# from models import Discount, Price

def handle_start_date(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    current_state = bot.get_state(user_id, chat_id)

    start_date = text_accept(message)
    try:
        start_date_obj = datetime.strptime(start_date, '%d.%m.%y')
    except Exception as e:
        # print(f'Что то пошло не так {e}')
        # pass
        start_date_obj = None
        logger.error(f'Ошибка handle_start_date [{e}]')

    if not start_date or not start_date_obj:
        bot.send_message(
            chat_id, '<b>Неправильный формат</b> даты начала (<b>требуется DD.MM.YY</b>), введите дату в правильном формате',
            reply_markup=kb_statistics_back())
        return

    # DATE_FORMAT
    # value = datetime(year, month, day)
    # value = datetime.now()

    # datetime_pattern = r'^(0?[1-9]|[1-2]\d|3[0-1])[ .]+(0?[1-9]|1[0-2])(?:[ .]+(\d{4}|\d{2}))?(?:[ ]+([0-1]?\d|2[0-3])[: ]+([0-5]?\d))?$'
    # value = re.search(datetime_pattern, mes_text)
    # mes_text = text_accept(message) or '-'
    # day = int(value.group(1))
    # month = int(value.group(2))
    # year = value.group(3)
    # year = datetime.now().year

    # with bot.retrieve_data(user_id, chat_id) as data:
    #     kind = data.get('kind')
    #     post: Post = data.get('post')
    #     post.date_time = value
    
    if current_state == 'AdminStatisticsState:start_date':
        set_state_data(bot, user_id, chat_id, {'start_date_obj': start_date_obj})
        # Запрашиваем дату окончания
        bot.send_message(
            chat_id,
            "Введите дату ОКОНЧАНИЯ ПЕРИОДА в формате DD.MM.YY",
            reply_markup=kb_statistics_back()
        )

        bot.set_state(user_id, AdminStatisticsState.fin_date, chat_id)

    if current_state == 'AdminStatisticsState:start_date_only':
        # Фильтруем по заданной стартовой и текущей дате - результат - вывод пользователей
        start_date_filter = start_date_obj.strftime(DATE_FORMAT)
        fin_date_filter = datetime.utcnow()

        date_start_show = start_date_obj.strftime(PRINT_DATE_FROMAT)
        date_fin_show = datetime.now().strftime(PRINT_DATE_FROMAT)

        bot.send_message(
            chat_id,
            f"Список клиентов с платежами, за выбранный период c {date_start_show} по {date_fin_show} :",
            reply_markup=None
        )
        base_statis.show_paid_users(message, start_to_fin=f'{start_date_filter}|{fin_date_filter}')
        bot.send_message(
            chat_id,
            "Вернуться:",
            reply_markup=kb_statistics_back()
        )

        bot.delete_state(user_id, chat_id)


def handle_fin_date(message: Message, bot: TeleBot):
    chat_id = message.chat.id
    user_id = message.from_user.id

    fin_date = text_accept(message)
    try:
        fin_date_obj = datetime.strptime(fin_date, '%d.%m.%y')
    except Exception as e:
        fin_date_obj = None
        logger.error(f'Ошибка handle_fin_date [{e}]')

    if not fin_date or not fin_date_obj:
        bot.send_message(
            chat_id, '<b>Неправильный формат</b> даты ОКОНЧАНИЯ ПЕРИОДА (<b>требуемый DD.MM.YY</b>), введите дату в правильном формате',
            reply_markup=kb_statistics_back())
        return

    with bot.retrieve_data(user_id, chat_id) as data:
        start_date_obj = data.get('start_date_obj')

    start_date_filter = start_date_obj.strftime(DATE_FORMAT)
    fin_date_filter = fin_date_obj.strftime(DATE_FORMAT)

    date_start_show = start_date_obj.strftime(PRINT_DATE_FROMAT)
    date_fin_show = datetime.now().strftime(PRINT_DATE_FROMAT)

    bot.send_message(
        chat_id,
        f"Список клиентов с платежами, за выбранный период c {date_start_show} по {date_fin_show} :",
        reply_markup=None
    )
    base_statis.show_paid_users(message, start_to_fin=f'{start_date_filter}|{fin_date_filter}')
    bot.send_message(
        chat_id,
        "Вернуться:",
        reply_markup=kb_statistics_back()
    )

    bot.delete_state(user_id, chat_id)

def registration(bot: TeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_start_date, state=AdminStatisticsState.start_date)
    reg_mes(handle_start_date, state=AdminStatisticsState.start_date_only)
    reg_mes(handle_fin_date, state=AdminStatisticsState.fin_date)

