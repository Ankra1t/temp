from telebot import TeleBot
from telebot.types import CallbackQuery

from db import db
from db_new import db_new

# TODO удалить
from initialize import text_editor
from initialize import pay_guard

from common.utils import set_state_data
from MAIN.states import AdminParamsState
from messages.workers import menu_msg

from .keyboards import kb_calculator, kb_params_back, kb_params_change, kb_params
from .filter import admin_params_factory, AdminParamsCallbackFilter


def _handle_callback(call: CallbackQuery, bot: TeleBot):
    callback_data: dict = admin_params_factory.parse(call.data)
    type = callback_data['type']

    chat_id = call.message.chat.id
    user_id = call.from_user.id
    mes_id = call.message.id

    if type == 'calculator':
        sup = db_new.get_support_name()
        sup_link = f'@{sup}' if (sup != '') else ''

        bot.edit_message_text(
            f'<b>Калькулятор расчета рисков</b>\nТех.поддержка: {sup_link}',
            chat_id, mes_id,
            reply_markup=kb_calculator()
        )

    elif type == 'update_texts':
        text_editor.list_texts(call.message.chat)
        bot.send_message(
            chat_id, 'Выберите текст для редактирования 👆',
            reply_markup=kb_params_back()
        )

    elif type == 'change_trial_days':
        days = pay_guard.get_option_trial_days()
        bot.edit_message_text(
            f'Сейчас для нового пользователя кол-во дней пробного периода {days}дн. '
            f'\n\n'
            f'Отправьте новое значение дней:', chat_id, mes_id,
            reply_markup=kb_params_back()
        )
        bot.set_state(user_id, AdminParamsState.count_trial_days, chat_id)

    elif type == 'show':
        # todo-fin: Что-то тут не работает, что-то достается из БД
        # mas = db.get_other()
        # for i in range(0, len(mas)):
        #     bot.send_message(message.chat.id, text=mas[i][0] + '\n---------------\n' + mas[i][1])
        # bot.register_next_step_handler(message, admin_other_menu)
        pass
    elif type == 'change':
        bot.edit_message_text(
            'Что изменяем?', chat_id, mes_id,
            reply_markup=kb_params_change())



    elif 'choice' in type:
        if 'yes' in type:
            with bot.retrieve_data(user_id, chat_id) as data:
                name = data.get('name', '')
                text = data.get('text', '')

            db_new.update_text(name, text)

            bot.send_message(chat_id, 'Успешно')
            bot.send_message(
                chat_id, menu_msg('Параметры'),
                reply_markup=kb_params())
        if 'no' in type:
            bot.edit_message_text(
                'Что изменяем?', chat_id, mes_id,
                reply_markup=kb_params_change())
        bot.delete_state(user_id, chat_id)

    elif 'change' in type:
        name = 'FAQ' if 'faq' in type else 'О нас'
        text = f'Отправьте новый текст {name}'

        bot.edit_message_text(
            text, chat_id, mes_id,
            reply_markup=kb_params_back())
        bot.set_state(user_id, AdminParamsState.text, chat_id)
        set_state_data(bot, user_id, chat_id, {'name': name})
    elif 'calculator' in type:
        if 'add_future' in type:
            bot.edit_message_text(
                'Введите тикер фьючерса:', chat_id, mes_id,
                reply_markup=kb_params_back()
            )
            bot.set_state(user_id, AdminParamsState.future_name, chat_id)
        if 'add_forex' in type:
            bot.edit_message_text(
                'Введите валютную пару:', chat_id, mes_id,
                reply_markup=kb_params_back()
            )
            bot.set_state(user_id, AdminParamsState.forex_paire, chat_id)

    bot.answer_callback_query(call.id)


def registration(bot: TeleBot):
    bot.add_custom_filter(AdminParamsCallbackFilter())
    bot.register_callback_query_handler(
        _handle_callback,
        lambda _: True, pass_bot=True,
        admin_params=admin_params_factory.filter())
