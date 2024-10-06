from db import db
import requests
from config_logger import logger

session = requests.Session()
session.headers.update({
    'Accept': 'application/json, text/plain, */*'
})


def session_decorator(func):
    def wrapper(*args, **kwargs):
        access_token = db.get_access_token() or ''
        session.headers.update({
            'tg-api-key': access_token
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
