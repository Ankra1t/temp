from telebot import types
from cb_filters import (admin_default_factory, adm_action, client_action,
                        admin_main_factory, admin_workerss_factory)


class Admin_kb_inlines(object):

    def __init__(self) -> None:
        self.dt_format = "%Y-%m-%d %I:%M"
        self.go_main_btn = types.InlineKeyboardButton(
            '🔙 Главная', callback_data=admin_default_factory.new(type='go_main'))
        self.go_users_btn = types.InlineKeyboardButton(
            '🔙 Пользователи', callback_data=admin_main_factory.new(type='users'))
        self.go_fut_posts_btn = types.InlineKeyboardButton(
            '🔙 Отложенные посты', callback_data=admin_main_factory.new(type='fut_posts'))
        self.go_params_btn = types.InlineKeyboardButton(
            '🔙 Параметры', callback_data=admin_main_factory.new(type='params'))

        self.go_workers_btn = types.InlineKeyboardButton(
            '🔙 Работники', callback_data=admin_main_factory.new(type='workers'))
        self.go_workers_redactors_btn = types.InlineKeyboardButton(
            '🔙 Редакторы', callback_data=admin_workerss_factory.new(type='redactors'))
        self.go_workers_admins_btn = types.InlineKeyboardButton(
            '🔙 Гл. админы', callback_data=admin_workerss_factory.new(type='admins'))
        self.go_workers_support_btn = types.InlineKeyboardButton(
            '🔙 Тех. поддержка', callback_data=admin_workerss_factory.new(type='support'))

    # Главная
    def main(self):
        def getCbData(type: str):
            return admin_main_factory.new(type=type)

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        btn1 = types.InlineKeyboardButton("Пользователи",
                                          callback_data=getCbData('users'))
        btn2 = types.InlineKeyboardButton("Работники",
                                          callback_data=getCbData('workers'))
        btn3 = types.InlineKeyboardButton("Отложенные посты",
                                          callback_data=getCbData('fut_posts'))
        btn4 = types.InlineKeyboardButton("Оплата",
                                          callback_data=getCbData('payment'))
        btn5 = types.InlineKeyboardButton("Параметры",
                                          callback_data=getCbData('params'))
        btn6 = types.InlineKeyboardButton("Тарифы",
                                          callback_data=getCbData('tariffs'))
        # btn3 = types.InlineKeyboardButton("Постинг")
        # btn5 = types.InlineKeyboardButton("Другое")
        # btn6 = types.InlineKeyboardButton("Главная")
        # btn7 = types.InlineKeyboardButton("Live пост ⚡️")
        keyboard.add(btn1, btn2)
        keyboard.add(btn3, btn4)
        keyboard.add(btn5, btn6)
        return keyboard

    # Меню Работники
    def workers(self):
        def getCbData(type: str):
            return admin_workerss_factory.new(type=type)

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        btn1 = types.InlineKeyboardButton('Гл.админы',
                                          callback_data=getCbData('admins'))
        btn2 = types.InlineKeyboardButton('Редакторы',
                                          callback_data=getCbData('redactors'))
        btn3 = types.InlineKeyboardButton('Тех.поддержка',
                                          callback_data=getCbData('support'))
        btn4 = types.InlineKeyboardButton('Список раб.',
                                          callback_data=getCbData('workers_list'))
        btn6 = self.go_main_btn

        keyboard.add(btn1, btn2)
        keyboard.add(btn3, btn4)
        keyboard.add(btn6)
        return keyboard

    def workers_actions_back(self, worker: str):
        keyboard = types.InlineKeyboardMarkup(row_width=2)

        back_btn = self.go_workers_btn
        if worker == 'support':
            back_btn = self.go_workers_support_btn
        if worker == 'redactor':
            back_btn = self.go_workers_redactors_btn
        if worker == 'admin':
            back_btn = self.go_workers_admins_btn

        keyboard.add(back_btn, self.go_main_btn)
        return keyboard

    # TODO - переиминовать + создать отдельный factory
    def workers_choice(self, action: str):
        def getCbData(type: str):
            return admin_default_factory.new(type=f'{action}_{type}')

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        yes = types.InlineKeyboardButton('Да',
                                         callback_data=getCbData('yes'))
        no = types.InlineKeyboardButton('Нет',
                                        callback_data=getCbData('no'))

        keyboard.add(yes, no)
        return keyboard

    def workers_support(self):
        def getCbData(type: str):
            return admin_default_factory.new(type=type)

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        btn = types.InlineKeyboardButton('Изменить',
                                         callback_data=getCbData('update_support'))

        keyboard.add(btn, self.go_workers_btn)
        return keyboard

    # Управление баном пользователя
    def user_unbun(self, user_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        unban_user = types.InlineKeyboardButton(text='Разбанить',
                                                callback_data=adm_action.new(action='unban_user', id=user_id))

        keyboard.add(unban_user)
        return keyboard

    def kb_success_ban_actions(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        menu_users = self.go_users_btn
        go_main = self.go_main_btn
        ban_list = types.InlineKeyboardButton(text='Список бана',
                                              callback_data=admin_default_factory.new(type='ban_list'))

        keyboard.add(menu_users, go_main)
        keyboard.add(ban_list)
        return keyboard

    # Отмена подписки
    def users_cancel_subscribe(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        subscribe_cancel_time = types.InlineKeyboardButton(
            'За период', callback_data=admin_default_factory.new(type='subscribe_cancel_time'))
        subscribe_cancel_user = types.InlineKeyboardButton(
            'Для пользователя', callback_data=admin_default_factory.new(type='subscribe_cancel_user'))

        keyboard.add(subscribe_cancel_time, subscribe_cancel_user)
        keyboard.add(self.go_users_btn, self.go_main_btn)
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
        keyboard.add(self.go_users_btn, self.go_main_btn)
        return keyboard

    def users_cancel_subscribe_user(self, user_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        user_cancel_subscribe = types.InlineKeyboardButton(
            'Отменить подписку', callback_data=adm_action.new(action='user_cancel_subscribe', id=user_id))
        admin_change_subscribe_for_user = types.InlineKeyboardButton(
            'Выбрать другую', callback_data=adm_action.new(action='admin_change_subscribe_for_user', id=user_id))

        keyboard.add(user_cancel_subscribe, admin_change_subscribe_for_user)
        keyboard.add(self.go_users_btn, self.go_main_btn)

        return keyboard

    # Редактирование текста клавиатуры
    def kb_edit_single_text(self, text_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        edit = types.InlineKeyboardButton(text='Редактировать ✏️',
                                          callback_data=adm_action.new(action='edit_bot_text', id=text_id))
        keyboard.add(edit)
        return keyboard

    def kb_edit_single_text_cancel(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        cancel = types.InlineKeyboardButton(text='Отменить редактирование',
                                            callback_data=admin_default_factory.new(type='go_main'))
        keyboard.add(cancel)
        return keyboard

    def kb_edit_single_text_updated(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        go_main = types.InlineKeyboardButton(text='🔙 Главная',
                                             callback_data=admin_default_factory.new(type='go_main'))

        bot_texts_list = types.InlineKeyboardButton(text='Список текстов',
                                                    callback_data=adm_action.new(action='bot_texts_list', id=''))
        keyboard.add(go_main, bot_texts_list)
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
        keyboard.add(self.go_main_btn)
        return keyboard

    def kb_tariffs_back_cancel(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        tariffs_list = types.InlineKeyboardButton(text='🔙 Список тарифов',
                                                  callback_data=admin_default_factory.new(type='tariffs_list'))

        keyboard.add(tariffs_list, self.go_main_btn)
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
        keyboard.add(self.go_main_btn)
        return keyboard

    def kb_tariff_options(self, tariff_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        deactivate_tariff = types.InlineKeyboardButton(text='Удалить ❌',
                                                       callback_data=adm_action.new(action='deactivate_tariff', id=tariff_id))
        add_discount_tariff = types.InlineKeyboardButton(text='Добавить скидку 🏷',
                                                         callback_data=adm_action.new(action='add_discount_tariff', id=tariff_id))
        edit_tariff = types.InlineKeyboardButton(text='Редактировать тариф ✏️',
                                                         callback_data=adm_action.new(action='edit_tariff',
                                                                                      id=tariff_id))

        keyboard.add(deactivate_tariff, add_discount_tariff)
        keyboard.add(edit_tariff)
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
        go_main = self.go_main_btn
        tariffs_list = types.InlineKeyboardButton(text='🔙 Список тарифов',
                                                  callback_data=admin_default_factory.new(type='tariffs_list'))


        keyboard.add(change_tariff_name, change_tariff_description)
        keyboard.add(change_tariff_price, change_tariff_duration)
        keyboard.add(change_tariff_image)
        keyboard.add(go_main, tariffs_list)
        return keyboard

    def kb_tariff_options_choose(self, user_tariff):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        admin_set_tariff_client = types.InlineKeyboardButton(text='Установить',
                                                             callback_data=adm_action.new(action='admin_set_tariff_client',
                                                                                          id=user_tariff))

        keyboard.add(admin_set_tariff_client)
        return keyboard

    def kb_add_sub_subscribe(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        add_days = types.InlineKeyboardButton(text='Добавить',
                                              callback_data=admin_default_factory.new(type='add_days_subscribe'))
        deduct_days = types.InlineKeyboardButton(text='Убрать',
                                                 callback_data=admin_default_factory.new(type='deduct_days_subscribe'))

        keyboard.add(add_days, deduct_days)
        keyboard.add(self.go_users_btn)
        return keyboard


class Clients_kb_inlines(object):
    def __init__(self) -> None:
        self.dt_format = "%Y-%m-%d %I:%M"

    # ## Клиент нажал купить
    def kb_pay(self, tariff_id, user_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        pay_tariff = types.InlineKeyboardButton(text='Купить',
                                                callback_data=client_action.new(
                                                    action='pay_tariff',
                                                    id=tariff_id,
                                                    user_id=user_id))

        keyboard.add(pay_tariff)
        return keyboard

    # ## Клиенту выставлен счет через Cryptobot со ссылкой оплаты
    def kb_bill(self, price, pay_link):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        pay_link_btn = types.InlineKeyboardButton(
            text=f"Оплатить {price} через CryptoBot", url=pay_link)
        keyboard.add(pay_link_btn)
        return keyboard

    # ## Клиенту выставлен счет через BitBanker и Cryptobot со ссылками оплаты
    def kb_bill_many(self, price, pay_link1, pay_link2):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        pay_link_btn1 = types.InlineKeyboardButton(
            text=f"Оплатить {price} через CryptoBot", url=pay_link1)
        pay_link_btn2 = types.InlineKeyboardButton(
            text=f"Оплатить {price} через BitBanker", url=pay_link2)

        keyboard.add(pay_link_btn1)
        keyboard.add(pay_link_btn2)
        return keyboard

    # ## Клиенту выставлен счет через BitBanker со ссылкой оплаты
    def kb_bill_bitbanker(self, price, pay_link2):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        pay_link_btn2 = types.InlineKeyboardButton(
            text=f"Оплатить {price}", url=pay_link2)

        keyboard.add(pay_link_btn2)
        return keyboard

    # ## Клиенту выставлен счет через BitBanker со ссылкой оплаты
    # def kb_bill_bb(self, price, pay_link):
    #     keyboard = types.InlineKeyboardMarkup(row_width=2)
    #     pay_link_btn = types.InlineKeyboardButton(
    #         text=f"Оплатить {price} через BitBanker", url=pay_link)
    #     keyboard.add(pay_link_btn)
    #     return keyboard
