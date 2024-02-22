def default_menu(name: str):
    return '\n'.join((
        f'<b>{name}</b>',
        '',
        'Выберите:'
    ))


def msg_referral(ref_count: int, bot_name: str, user_id: int):
    return f"""
<b>Сейчас у вас:</b> {ref_count} реферал(ов)
<b>Скопируйте</b> ссылку ниже и поделитесь ей со своими друзьями😌
В будущем Вы будете получать <b>вознаграждение</b> за активность ваших рефералов😉

https://t.me/{bot_name}/?start={user_id}
"""
