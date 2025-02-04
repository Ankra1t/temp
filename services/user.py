import json
from models import RefUser
from services.base_config import check_response, session_decorator, session
from config_global import API_URL


@session_decorator
def getReferralOfUser(userId: int):
    res = session.get(
        f'{API_URL}/users/{userId}/referral',
    )

    if not check_response(res):
        return

    if res.text != '':
        return RefUser.model_validate_json(res.text)


@session_decorator
def update(
    *,
    userId: int,
    tgUsername: str
):
    data = {
        "tgUsername": tgUsername
    }

    res = session.post(
        f'{API_URL}/users/{userId}',
        json.dumps(data).encode()
    )
    if not check_response(res):
        return

    return True
