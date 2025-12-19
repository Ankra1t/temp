from config_global import CURRENCYAPI_KEY

from db import db

from .HTML2Image import HTIService
from .GuardPaymentAccess import GuardPaymentAccess
from .TextEditor import TextEditor
from .BaseStatistics import BaseStatistics
from .CalculationService import CalculationService
from .CurrencyService import CurrencyService
from .BlockTGBotSender import send_same_message_to_users  # type: ignore

pay_guard = GuardPaymentAccess()
base_statis = BaseStatistics(db)

currencyService = CurrencyService(CURRENCYAPI_KEY)
calcService = CalculationService(db, currencyService)

hti = HTIService(calcService)
text_editor = TextEditor()
