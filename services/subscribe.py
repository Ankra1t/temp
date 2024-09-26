import json
from typing import TypedDict
from typing_extensions import Unpack, NotRequired

from models import PRODUCT_TYPE
from services.base_config import check_response, session_decorator, session
from config_global import API_URL


class CreateSub(TypedDict):
    userId: int
    productType: PRODUCT_TYPE
    finishMinutes: NotRequired[int]


@session_decorator
def check(userId: int, productType: PRODUCT_TYPE) -> bool | None:
    res = session.get(
        f'{API_URL}/subscribe/check?userId={userId}&productType={productType}',
    )

    if not check_response(res):
        return

    return res.json()


@session_decorator
def create(
    **kwargs: Unpack[CreateSub],
):
    res = session.post(
        f'{API_URL}/subscribe',
        json.dumps(kwargs).encode()
    )

    if not check_response(res):
        return

    return True
