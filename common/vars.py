from config_global import _ENV

DATE_FORMAT = '%Y-%m-%d %H:%M'

if _ENV == 'prod':
    API_URL = 'https://my-traders.com/api'
else:
    API_URL = 'http://127.0.0.1:8000/api'

if _ENV == 'prod':
    SITE_URL = 'https://my-traders.com/_test_frontend'
else:
    SITE_URL = 'http://127.0.0.1:3000'

HEADERS = {
    'content-type': 'application/json',
    'Accept': 'application/json, text/plain, */*'
}
