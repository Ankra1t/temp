from db import db
import requests

session = requests.Session()
session.headers.update({
    'content-type': 'application/json',
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
            print(e)
            return

        return result

    return wrapper


def check_response(res: requests.Response):
    if res.status_code < 200 or res.status_code > 299:
        print(res.status_code)
        print(res.json())
        return False
    return True
