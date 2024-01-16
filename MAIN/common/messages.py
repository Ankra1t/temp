def default_menu(name: str):
    return '\n'.join((
        f'<b>{name}</b>',
        '',
        'Выберите:'
    ))


def msg_referral(count: int):
    return f"""
<b>Сейчас у вас:</b> {count} реферал(ов)
<b>Скопируйте</b> ссылку ниже и поделитесь ей со своими друзьями😌
В будущем Вы будете получать <b>вознаграждение</b> за активность ваших рефералов😉

https://t.me/peoplestest_bot/?start={id}
"""