from telebot.async_telebot import AsyncTeleBot

from messages.errors import msg_digit_error
from models import Message, StateContext, User

from common.utils import digit_accept

from pages.calculate import send_admin_channel_calc_item, send_admin_send_settings, send_confirm_calc_send
from service.advanced_settings_storage import advanced_settings_storage
from states.admin_params import AdminParamsState


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
        type = data.get('type')

    if calc_id is None:
        advanced_settings_storage.update_advanced(
            user.id, trailingStop=value, autoTake=None)
        await send_admin_send_settings(bot, message, state, user, True)
    else:
        # TODO - calculation.updateActive(userId=user.id, id=calc_id, trailingStopCount=value, autoTake=None)

        if type == 'change_sent':
            await send_admin_channel_calc_item(
                bot, message, state, calc_id, is_first=True
            )
        else:
            await send_confirm_calc_send(bot, message, calc_id, True)


def registration(bot: AsyncTeleBot):
    def reg_mes(handler, **kwargs):
        bot.register_message_handler(handler, pass_bot=True, **kwargs)

    reg_mes(handle_trailing_stop, state=AdminParamsState.trailing_stop)
