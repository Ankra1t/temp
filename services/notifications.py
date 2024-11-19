
from io import BufferedReader
from typing import Optional, TypedDict
from typing_extensions import Unpack, NotRequired
from config_global import API_URL
from services.base_config import check_response, session_decorator, session


class CreateNotification(TypedDict):
    title: str
    text: NotRequired[Optional[str]]
    file: NotRequired[Optional[BufferedReader]]


@session_decorator
def create(
    *,
    userId: int,
    **data: Unpack[CreateNotification]
):
    file = data['file'] if 'file' in data else None

    body = {
        'title': data['title'],
    }
    if 'text' in data and data['text']:
        body['text'] = data['text']

    res = session.post(
        f'{API_URL}/notification',
        files={'file': file} if file else None,
        data=body,
        headers={
            'content-type': None
        }
    )

    if not check_response(res):
        return

    return True
