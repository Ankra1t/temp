import requests
from config_logger import logger
from config_global import API_AUTH_KEY

session = requests.Session()
session.headers.update({
    'content-type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'tg-api-key': API_AUTH_KEY,
})


def session_decorator(func):
    def wrapper(*args, **kwargs):
        userId = kwargs.get('userId') or 1
        if userId:
            session.headers.update({
                'tg-user-id': str(userId)
            })

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(e)
            return

        return result

    return wrapper


def check_response(res: requests.Response):
    if res.status_code < 200 or res.status_code > 299:
        logger.error(f'Service error ({res.status_code}): {res.text}')
        return False
    return True
