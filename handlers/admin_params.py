from telebot.async_telebot import AsyncTeleBot

from keyboards.admin_main import kb_tools_list_back
from messages.errros import msg_digit_error
from models import Message, StateContext, User
from Classes import pay_guard

from common.utils import digit_accept, get_print_float, get_normal_text

from pages.admin import send_admin_tools_list
from pages.calculate import send_admin_send_settings, send_confirm_calc_send
from services import calculation, settings
from states.admin_params import AdminMainState, AdminParamsState
from keyboards.admin_params import kb_params_choice, kb_params_back


_pair_pattern = r'^[a-zA-Z]{3}/[a-zA-Z]{3}$'


async def handle_other_text(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id

    await state.add_data(
        text=get_normal_text(message)
    )

    await bot.send_message(
        chat_id, 'Применить изменения?',
        reply_markup=kb_params_choice('change')
    )


async def handle_count_trial_days(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id

    count_days = digit_accept(message, int)
    if count_days is None:
        await bot.send_message(
            chat_id, 'Введите число:',
            reply_markup=kb_params_back())
        return

    # Сохраняем данные тарифа в таблице параметров
    pay_guard.set_option_trial_days(count_days)

    await bot.send_message(
        chat_id, f'✅ Кол-во пробных дней {int(count_days)}дн. для нового пользователя сохранено',
        reply_markup=kb_params_back()
    )

    await state.delete()


async def handle_turnover(message: Message, bot: AsyncTeleBot, state: StateContext):
    chat_id = message.chat.id

    turnover = digit_accept(message)
    if turnover is None:
        new_mes = await bot.send_message(
            chat_id, 'Введите значение числом:',
            reply_markup=kb_tools_list_back()
        )
        await state.add_data(del_mes_id=new_mes.id)
        return

    turnover = get_print_float(turnover, 1)

    await send_admin_tools_list(bot, message, turnover, True)


async def handle_trailing_stop(message: Message, bot: AsyncTeleBot, state: StateContext, user: User):
    chat_id = message.chat.id

    value = digit_accept(message)
    if value is None:
        new_mes = await bot.send_message(
            chat_id, msg_digit_error('ru')
        )
        await state.add_data(
            del_mes_id=new_mes.id
        )
        return

    value = round(value, 1)

    async with state.data() as data:
        calc_id = data.get('calc_id')

    if calc_id is None:
        settings.updateAdvanced(user.id, trailingStop=value)
        await send_admin_send_settings(bot, message, state, user, True)
    else:
        calculation.updateTrailingStop(
            calc_id, value
        )
        await send_confirm_calc_send(bot, message, calc_id, True)



def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_other_text, state=AdminParamsState.text)

    reg_mes(handle_count_trial_days, state=AdminParamsState.count_trial_days)

    reg_mes(handle_trailing_stop, state=AdminParamsState.trailing_stop)

    reg_mes(handle_turnover, state=AdminMainState.turnover)
