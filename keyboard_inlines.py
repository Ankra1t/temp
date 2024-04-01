from telebot import types
from cb_filters import (
    admin_default_factory, adm_action
)


class Admin_kb_inlines(object):

    def __init__(self) -> None:
        pass

    # Отмена подписки
    def users_cancel_subscribe(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        subscribe_cancel_time = types.InlineKeyboardButton(
            'За период', callback_data=admin_default_factory.new(type='subscribe_cancel_time'))
        subscribe_cancel_user = types.InlineKeyboardButton(
            'Для пользователя', callback_data=admin_default_factory.new(type='subscribe_cancel_user'))

        keyboard.add(subscribe_cancel_time, subscribe_cancel_user)
        # keyboard.add(self.go_users_btn) # !!! Кнопка назад
        return keyboard

    def users_cancel_subscribe_time(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        cancel_subscribe_hour = types.InlineKeyboardButton('За час',
                                                           callback_data=admin_default_factory.new(type='cancel_subscribe_hour'))
        cancel_subscribe_day = types.InlineKeyboardButton('За день',
                                                          callback_data=admin_default_factory.new(type='cancel_subscribe_day'))
        cancel_subscribe_period = types.InlineKeyboardButton('Указать период',
                                                             callback_data=admin_default_factory.new(type='cancel_subscribe_period'))

        keyboard.add(cancel_subscribe_hour, cancel_subscribe_day)
        keyboard.add(cancel_subscribe_period)
        # keyboard.add(self.go_users_btn) # !!! Кнопка назад
        return keyboard

    def users_cancel_subscribe_user(self, user_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        user_cancel_subscribe = types.InlineKeyboardButton(
            'Отменить подписку', callback_data=adm_action.new(action='user_cancel_subscribe', id=user_id))
        admin_change_subscribe_for_user = types.InlineKeyboardButton(
            'Выбрать другую', callback_data=adm_action.new(action='admin_change_subscribe_for_user', id=user_id))

        keyboard.add(user_cancel_subscribe, admin_change_subscribe_for_user)
        # keyboard.add(self.go_users_btn) # !!! Кнопка назад

        return keyboard

    def kb_tariff_options_choose(self, user_tariff):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        admin_set_tariff_client = types.InlineKeyboardButton(
            'Установить',
            callback_data=adm_action.new(
                action='admin_set_tariff_client', id=user_tariff
            )
        )

        keyboard.add(admin_set_tariff_client)
        return keyboard

    def kb_tariff_choose_for_user(self, tariff_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        admin_set_tariff_client = types.InlineKeyboardButton(
            'Выбрать для пользователя',
            callback_data=adm_action.new(
                action='admin_set_tariff_client',
                id=tariff_id
            )
        )

        keyboard.add(admin_set_tariff_client)
        return keyboard
