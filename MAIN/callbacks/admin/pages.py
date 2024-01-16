from telebot import TeleBot, REPLY_MARKUP_TYPES


def send_admin_post(
    bot: TeleBot, chat_id: int, id,
    media, text, direct, date, time, kind,
    open_price, stop_loss, name
):
    signal_txt = '\n'.join((
        f'Цена входа: <b>{open_price}</b>' if open_price is not None else '',
        f'Стоп лосс: <b>{stop_loss}</b>' if stop_loss is not None else '',
    )) if kind == 'signal' else ''

    result = signal_txt + '\n'.join((
        f'<b>{name}</b>' if name is not None else '',
        signal_txt,
        '',
        text,
        '',
        f'ID: <b>{id}</b>',
        f'Тип: <b>{"Сигнал" if kind == "signal" else "Пост"}</b>',
        f'Время поста: <b>{time}</b>',
        f'Дата: <b>{date}</b>',
        f'Ограничение: <b>{direct}</b>',
    ))

    if '(text)' in media:
        bot.send_message(chat_id, result)
    elif '(photo)' in media:
        out_file = media.replace('(photo)', '')
        bot.send_photo(
            chat_id, out_file,
            caption=result
        )
    elif '(video)' in media:
        out_file = media.replace('(video)', '')
        bot.send_video(
            chat_id, out_file,
            caption=result
        )
