from Classes.CoinmarketService import CoinmarketService
from config_global import COINMARKET_KEY, CURRENCYAPI_KEY

from db import db

from .HTML2Image import HTIService
from .GuardPaymentAccess import GuardPaymentAccess
from .TariffManager import TariffManager
from .TextEditor import TextEditor
from .BaseStatistics import BaseStatistics
from .ServiceTasks import ServiceTasks
from .CalculationService import CalculationService
from .CurrencyService import CurrencyService
from .SharesService import SharesService
from .BlockTGBotSender import send_same_message_to_users # type: ignore

pay_guard = GuardPaymentAccess()
base_statis = BaseStatistics(db)
serv_tasks = ServiceTasks(db)

currencyService = CurrencyService(CURRENCYAPI_KEY)
calcService = CalculationService(db, currencyService)

hti = HTIService(calcService)
text_editor = TextEditor()
tariff_manager = TariffManager()

coinmarketService = CoinmarketService(COINMARKET_KEY)
sharesService = SharesService()