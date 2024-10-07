from io import BufferedReader

from services.base_config import check_response, session_decorator, session
from config_global import API_URL


@session_decorator
def create(
    file: BufferedReader
):
    res = session.post(
        f'{API_URL}/twitter',
        files={'file':  ('file.jpg', file, 'image/jpg')},
    )

    if not check_response(res):
        return

    return True
