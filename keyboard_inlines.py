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
        cancel_subscribe_hour = types.InlineKeyboardButton(text='За час',
                                                           callback_data=admin_default_factory.new(type='cancel_subscribe_hour'))
        cancel_subscribe_day = types.InlineKeyboardButton(text='За день',
                                                          callback_data=admin_default_factory.new(type='cancel_subscribe_day'))
        cancel_subscribe_period = types.InlineKeyboardButton(text='Указать период',
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

    # Меню Тарифы - добавление тарифов админом

    def kb_tariffs(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        tariffs_list = types.InlineKeyboardButton(text='Список тарифов',
                                                  callback_data=admin_default_factory.new(type='tariffs_list'))
        discount_list_active = types.InlineKeyboardButton(text='Скидки работают',
                                                          callback_data=admin_default_factory.new(type='discount_list_active'))
        discount_list_inactive = types.InlineKeyboardButton(text='Скидки прошли',
                                                            callback_data=admin_default_factory.new(type='discount_list_inactive'))
        add_tariff = types.InlineKeyboardButton(text='Добавить тариф',
                                                callback_data=admin_default_factory.new(type='add_tariff'))

        keyboard.add(tariffs_list, add_tariff)
        keyboard.add(discount_list_active, discount_list_inactive)
        # keyboard.add(self.go_main_btn) # !!! Кнопка назад
        return keyboard

    def kb_select_tariff_products(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        tariffs_list_all = types.InlineKeyboardButton(text='По всем продуктам',
                                                      callback_data=admin_default_factory.new(type='tariffs_list_all'))

        tariffs_list_by_product_signals = types.InlineKeyboardButton(text='📈 Рекомендация',
                                                                     callback_data=adm_action.new(
                                                                         action='tariffs_list_by_product',
                                                                         id='signals'))
        tariffs_list_by_product_calc = types.InlineKeyboardButton(text='🧮 Калькулятор',
                                                                  callback_data=adm_action.new(
                                                                      action='tariffs_list_by_product',
                                                                      id='calc'))
        tariffs_list_by_product_calc_signals = types.InlineKeyboardButton(text='Калькулятор + Рекомендация',
                                                                          callback_data=adm_action.new(
                                                                              action='tariffs_list_by_product',
                                                                              id='calc_signals'))

        keyboard.add(tariffs_list_all)
        keyboard.add(tariffs_list_by_product_signals,
                     tariffs_list_by_product_calc)
        keyboard.add(tariffs_list_by_product_calc_signals)
        # keyboard.add(self.go_main_btn) # !!! Кнопка назад
        return keyboard

    def kb_choice_product(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        tariffs_list = types.InlineKeyboardButton(text='Список тарифов',
                                                  callback_data=admin_default_factory.new(type='tariffs_list'))

        add_tariff_product_signals = types.InlineKeyboardButton(text='Рекомендация',
                                                                callback_data=adm_action.new(action='add_tariff_product',
                                                                                             id='signals'))
        add_tariff_product_calc = types.InlineKeyboardButton(text='Калькулятор',
                                                             callback_data=adm_action.new(
                                                                 action='add_tariff_product',
                                                                 id='calc'))
        add_tariff_product_calc_signals = types.InlineKeyboardButton(text='Калькулятор + Рекомендация',
                                                                     callback_data=adm_action.new(
                                                                         action='add_tariff_product',
                                                                         id='calc_signals'))

        keyboard.add(add_tariff_product_signals, add_tariff_product_calc)
        keyboard.add(add_tariff_product_calc_signals)
        keyboard.add(tariffs_list)
        return keyboard

    def kb_tariffs_back_cancel(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        tariffs_list = types.InlineKeyboardButton(text='🔙 Список тарифов',
                                                  callback_data=admin_default_factory.new(type='tariffs_list'))

        keyboard.add(tariffs_list)
        return keyboard

    def kb_tariff_list(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        tariffs_list = types.InlineKeyboardButton(text='Список тарифов',
                                                  callback_data=admin_default_factory.new(type='tariffs_list'))
        add_tariff = types.InlineKeyboardButton(text='Добавить тариф',
                                                callback_data=admin_default_factory.new(type='add_tariff'))
        discount_list_active = types.InlineKeyboardButton(text='Скидки работают',
                                                          callback_data=admin_default_factory.new(
                                                              type='discount_list_active'))
        discount_list_inactive = types.InlineKeyboardButton(text='Скидки прошли',
                                                            callback_data=admin_default_factory.new(
                                                                type='discount_list_inactive'))

        keyboard.add(tariffs_list, add_tariff)
        keyboard.add(discount_list_active, discount_list_inactive)
        # keyboard.add(self.go_main_btn) # !!! Кнопка назад
        return keyboard

    def kb_tariff_options(self, tariff_id, on_off_label='Отключить ⭕️'):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        deactivate_tariff = types.InlineKeyboardButton(text='Удалить ❌',
                                                       callback_data=adm_action.new(action='deactivate_tariff', id=tariff_id))
        add_discount_tariff = types.InlineKeyboardButton(text='Добавить скидку 🏷',
                                                         callback_data=adm_action.new(action='add_discount_tariff', id=tariff_id))
        edit_tariff = types.InlineKeyboardButton(text='Редактировать тариф ✏️',
                                                 callback_data=adm_action.new(action='edit_tariff',
                                                                              id=tariff_id))
        on_off_tariff = types.InlineKeyboardButton(text=f'{on_off_label}',
                                                   callback_data=adm_action.new(action='on_off_tariff',
                                                                                id=tariff_id))
        tempor_day_tariff = types.InlineKeyboardButton(text='Срок действия',
                                                       callback_data=adm_action.new(action='tempor_day_tariff',
                                                                                    id=tariff_id))

        keyboard.add(deactivate_tariff, add_discount_tariff)
        keyboard.add(edit_tariff, on_off_tariff)
        keyboard.add(tempor_day_tariff)
        return keyboard

    def kb_change_tariff_fields(self, tariff_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        change_tariff_name = types.InlineKeyboardButton(text='Название',
                                                        callback_data=adm_action.new(action='change_tariff_name', id=tariff_id))
        change_tariff_description = types.InlineKeyboardButton(text='Описание',
                                                               callback_data=adm_action.new(action='change_tariff_description',
                                                                                            id=tariff_id))
        change_tariff_price = types.InlineKeyboardButton(text='Стоимость',
                                                         callback_data=adm_action.new(
                                                             action='change_tariff_price',
                                                             id=tariff_id))
        change_tariff_duration = types.InlineKeyboardButton(text='Кол-во дней',
                                                            callback_data=adm_action.new(
                                                                action='change_tariff_duration',
                                                                id=tariff_id))

        change_tariff_image = types.InlineKeyboardButton(text='Постер (картинку)',
                                                         callback_data=adm_action.new(
                                                             action='change_tariff_image',
                                                             id=tariff_id))
        tariffs_list = types.InlineKeyboardButton(text='🔙 Список тарифов',
                                                  callback_data=admin_default_factory.new(type='tariffs_list'))

        keyboard.add(change_tariff_name, change_tariff_description)
        keyboard.add(change_tariff_price, change_tariff_duration)
        keyboard.add(change_tariff_image)
        keyboard.add(tariffs_list)
        return keyboard

    def kb_tariff_options_choose(self, user_tariff):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        admin_set_tariff_client = types.InlineKeyboardButton(text='Установить',
                                                             callback_data=adm_action.new(action='admin_set_tariff_client',
                                                                                          id=user_tariff))

        keyboard.add(admin_set_tariff_client)
        return keyboard

    def kb_tariff_choose_for_user(self, tariff_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        admin_set_tariff_client = types.InlineKeyboardButton(text='Выбрать для пользователя',
                                                             callback_data=adm_action.new(action='admin_set_tariff_client',
                                                                                          id=tariff_id))

        keyboard.add(admin_set_tariff_client)
        return keyboard

    def kb_tariff_findate(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        tariff_findate_period_day = types.InlineKeyboardButton(text='День', callback_data=adm_action.new(
            action='tariff_findate_period',
            id='day'
        ))
        tariff_findate_period_day3 = types.InlineKeyboardButton(text='3 дня', callback_data=adm_action.new(
            action='tariff_findate_period',
            id='day3'
        ))
        tariff_findate_period_week = types.InlineKeyboardButton(text='Неделя', callback_data=adm_action.new(
            action='tariff_findate_period',
            id='week'
        ))
        tariff_findate_period_month = types.InlineKeyboardButton(text='Месяц', callback_data=adm_action.new(
            action='tariff_findate_period',
            id='month'
        ))
        tariff_findate = types.InlineKeyboardButton(text='Задать дату окончания', callback_data=adm_action.new(
            action='tempor_day_tariff_count',
            id=''
        ))

        tariffs_list = types.InlineKeyboardButton(text='🔙 Список тарифов',
                                                  callback_data=admin_default_factory.new(type='tariffs_list'))

        keyboard.add(tariff_findate_period_day, tariff_findate_period_day3)
        keyboard.add(tariff_findate_period_week, tariff_findate_period_month)
        keyboard.add(tariff_findate)
        keyboard.add(tariffs_list)
        return keyboard

    def kb_add_sub_subscribe(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        add_days = types.InlineKeyboardButton(text='Добавить',
                                              callback_data=admin_default_factory.new(type='add_days_subscribe'))
        deduct_days = types.InlineKeyboardButton(text='Убрать',
                                                 callback_data=admin_default_factory.new(type='deduct_days_subscribe'))

        keyboard.add(add_days, deduct_days)
        # keyboard.add(self.go_users_btn) # !!! Кнопка назад
        return keyboard

