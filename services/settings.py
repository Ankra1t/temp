import json
from typing import Optional, TypedDict
from typing_extensions import Unpack, NotRequired

from models import AdvancedSettings
from services.base_config import check_response, session_decorator, session
from config_global import API_URL

class UpdateAdvancedSettings(TypedDict):
    autoOpen: NotRequired[Optional[bool]]
    autoStop: NotRequired[Optional[bool]]
    autoTake: NotRequired[Optional[float]]
    trailingStop: NotRequired[Optional[float]]
    cancelMinutes: NotRequired[Optional[float]]

@session_decorator
def getAdvanced(userId: int):
    res = session.get(
        f'{API_URL}/calc_settings/advanced/{userId}',
    )

    if not check_response(res):
        return

    return AdvancedSettings.model_validate_json(res.text)


@session_decorator
def updateAdvanced(
    userId: int,
    **kwargs: Unpack[UpdateAdvancedSettings],
):
    res = session.post(
        f'{API_URL}/calc_settings/advanced/{userId}',
        json.dumps(kwargs).encode()
    )

    if not check_response(res):
        return

    return AdvancedSettings.model_validate_json(res.text)
