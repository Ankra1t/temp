from config_global import CURRENCYAPI_KEY

from db import db

from .HTML2Image import HTIService
from .GuardPaymentAccess import GuardPaymentAccess
from .TariffManager import TariffManager
from .TextEditor import TextEditor
from .BaseStatistics import BaseStatistics
from .ServiceTasks import ServiceTasks
from .CalculationService import CalculationService
from .CurrencyService import CurrencyService




pay_guard = GuardPaymentAccess()
base_statis = BaseStatistics(db)
serv_tasks = ServiceTasks(db)

calcService = CalculationService(db)
currencyService = CurrencyService(CURRENCYAPI_KEY)

hti = HTIService()
text_editor = TextEditor()
tariff_manager = TariffManager()