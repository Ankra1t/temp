from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from db import db

from Classes import pay_guard

from common.utils import set_state_data
from states.admin_params import AdminParamsState

from keyboards.admin_params import (
    admin_params_factory, AdminParamsCallbackFilter,
    kb_calculator, kb_edit_text, kb_params_back, kb_params_change
)

from pages.admin import send_admin_main, send_admin_params


async def _handle_callback(call: CallbackQuery, bot: AsyncTeleBot):
    callback_data = admin_params_factory.parse(call.data)
    type = callback_data.get('type', '')

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'go_main':
        await send_admin_main(bot, call.message, user_id)

    if type == 'go_params':
        await send_admin_params(bot, call.message, user_id)

    if type == 'calculator':
        sup = db.get_support_name()
        sup_link = f'@{sup}' if (sup != '') else ''

        await bot.edit_message_text(
            f'<b>Калькулятор расчета рисков</b>\nТех. поддержка: {sup_link}',
            chat_id, mes_id,
            reply_markup=kb_calculator()
        )

    elif type == 'update_texts':
        texts = db.get_texts()
        if len(texts) != 0:
            for i in range(len(texts)):
                text = texts[i]
                text_show = f'ID: <b>{text.id}</b> | <b>{text.name}</b>\n\n{text.message}'

                await bot.send_message(
                    chat_id, text_show,
                    reply_markup=kb_edit_text(text.name)
                )

            await bot.send_message(
                chat_id, 'Выберите текст для редактирования 👆',
                reply_markup=kb_params_back()
            )
        else:
            await bot.send_message(
                chat_id, 'Текстов для редактирования не найдено',
                reply_markup=kb_params_back()
            )

    elif 'edit_text' in type:
        text_name = type.split('+')[-1]

        await bot.set_state(user_id, AdminParamsState.text, chat_id)
        await set_state_data(bot, user_id, chat_id, {
            'name': text_name
        })
        await bot.delete_message(chat_id, mes_id)
        await bot.send_message(
            chat_id,
            f'Отправьте новый текст для name={text_name}',
            reply_markup=kb_params_back()
        )

    elif type == 'change_trial_days':
        days = pay_guard.get_option_trial_days()
        await bot.edit_message_text(
            f'Сейчас для нового пользователя кол-во дней пробного периода {days}дн. '
            f'\n\n'
            f'Отправьте новое значение дней:', chat_id, mes_id,
            reply_markup=kb_params_back()
        )
        await bot.set_state(user_id, AdminParamsState.count_trial_days, chat_id)

    elif type == 'change':
        await bot.edit_message_text(
            'Что изменяем?', chat_id, mes_id,
            reply_markup=kb_params_change()
        )

    elif 'choice' in type:
        if 'yes' in type:
            async with bot.retrieve_data(user_id, chat_id) as data:
                name = data.get('name', '')
                text = data.get('text', '')

            db.update_text(name, text)

            await bot.send_message(chat_id, 'Успешно')
            await send_admin_params(bot, call.message, user_id, True)

        if 'no' in type:
            await bot.edit_message_text(
                'Что изменяем?', chat_id, mes_id,
                reply_markup=kb_params_change())
        await bot.delete_state(user_id, chat_id)

    elif 'change' in type:
        name = 'FAQ' if 'faq' in type else 'О нас'
        text = f'Отправьте новый текст {name}'

        await bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_params_back())
        await bot.set_state(user_id, AdminParamsState.text, chat_id)
        await set_state_data(bot, user_id, chat_id, {'name': name})

    elif 'calculator' in type:
        if 'add_forex' in type:  # !deprecated
            await bot.edit_message_text(
                'Введите валютную пару:', chat_id, mes_id,
                reply_markup=kb_params_back()
            )
            await bot.set_state(user_id, AdminParamsState.forex_pair, chat_id)

    await bot.answer_callback_query(call.id)


def registration(bot: AsyncTeleBot):
    bot.add_custom_filter(AdminParamsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback, # type: ignore
        lambda _: True, pass_bot=True,
        admin_params=admin_params_factory.filter())
