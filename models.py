from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message as _Message, User as _User, CallbackQuery as _CallbackQuery
from telebot.states.asyncio.context import StateContext as _StateContext
from telebot.asyncio_storage.base_storage import StateDataContext as _StateDataContext
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.asyncio_handler_backends import State
from telebot.states import resolve_context

from pydantic import BaseModel
from typing import Literal, Union, Optional
from datetime import datetime

SUBSCRIBE_TYPE = Literal['trial', 'PAID']
BASE_VALUE_TYPE = Literal['deposit', 'risk', 'currency']
SORT_BY_TYPE = Literal['new', 'old']

TRADING_TYPE = Literal["margin", "spot", "future"]
MARKETS_TYPE = Literal['crypto', 'paper', 'forex', 'RF', 'USA']
EXCHANGE_TYPE = Literal['BYBIT', 'BINANCE']
PRODUCT_TYPE = Literal['signals', 'calc', 'calc_signals', 'active_calc']
ROLE_TYPE = Literal['ADMIN', 'EDITOR', 'SUPPORT']
CALC_STATUS_TYPE = Literal['WAIT', 'CANCEL', 'FINISH', 'DEAL']

MANUAL_TYPE = Literal[
    'settings', 'exchange',
    'trading_type', 'trading_style', 'calc'
]

# Языки вывода
LANGUAGES_TYPE = Literal['ru', 'en', 'uz', 'tr']
LANGUAGES: tuple[LANGUAGES_TYPE, ...] = ('ru', 'en', 'uz', 'tr')

STYLES = {
    'Пробой': 'пробой уровня',
    'Отбой': 'отбой от уровня',
    'Ложные': 'ложные пробои',
    'Скользящие': 'скользящие средние',
    'High/low': 'торговля на high/low',
    'В канале': 'в канале',
}


class StateFilter(AdvancedCustomFilter):
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    key = 'state'

    async def check(self, message, text):
        if self.bot.bot_id is None or self.bot.current_states is None:
            return

        chat_id, user_id, business_connection_id, bot_id, message_thread_id = resolve_context(
            message, self.bot.bot_id
        )

        if chat_id is None:
            chat_id = user_id  # May change in future

        if isinstance(text, list):
            new_text = []
            for i in text:
                if isinstance(i, State):
                    i = i.name
                new_text.append(i)
            text = new_text
        elif isinstance(text, State):
            text = text.name

        user_state = await self.bot.current_states.get_state(
            chat_id=chat_id,
            user_id=user_id,
            business_connection_id=business_connection_id,  # type: ignore
            bot_id=bot_id,  # type: ignore
            message_thread_id=message_thread_id  # type: ignore
        )

        # CHANGED BEHAVIOUR
        if text == "*" and user_state is not None:
            return True

        if user_state == text:
            return True
        elif type(text) is list and user_state in text:
            return True
        return False


class StateContext(_StateContext):
    def data(self) -> _StateDataContext:
        return super().data()  # type: ignore


class Message(_Message):
    from_user: _User


class CallbackQuery(_CallbackQuery):
    message: Message


class Invoice(BaseModel):
    """Структура чека (deprecated)"""
    invoice_id: int
    status: str
    asset: str
    amount: Union[int, float]
    pay_url: str
    description: Optional[str] = None
    allow_comments: bool
    allow_anonymous: bool


class InvoiceBBanker(BaseModel):
    """(deprecated)"""
    invoice_id: Optional[int] = None
    status: Optional[str] = None
    asset: Optional[str] = None
    amount: Optional[Union[int, float]] = None
    pay_url: Optional[str] = None
    description: Optional[str] = None


class Update(BaseModel):
    """(deprecated)"""
    update_id: int
    update_type: str
    request_date: datetime
    payload: Invoice


class UpdateBBanker(BaseModel):
    """(deprecated)"""
    payload: InvoiceBBanker | None = None


class Subscribe(BaseModel):
    """(deprecated)"""
    id: int
    user_id: int
    finish_dt: datetime
    product_type: PRODUCT_TYPE
    active: bool
    transactions_payed_id: Optional[int] = None


class User(BaseModel):
    """Пользователь кратко"""
    id: int
    tgId: int
    lang: LANGUAGES_TYPE
    role: Literal[1, 0]


class Discount(BaseModel):
    """(deprecated)"""
    percent: float
    findate: datetime


class Price:
    """(deprecated)"""
    type_product: PRODUCT_TYPE

    def __init__(
        self,
        name: str,
        duration: int,
        price: int,
        currency: str,
        switch_active: bool,
        type_product: PRODUCT_TYPE,
        description: str,
        id: Optional[int] = None,
        image: Optional[str] = None,
        img_en: Optional[str] = None,
        discount_percent: Optional[float] = None,
        discount_findate: Optional[datetime] = None,
        price_findate: Optional[datetime] = None,
        price_crypto: Optional[float] = None,
        currency_crypto: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.currency = currency
        self.price = price
        self.duration_days = duration
        self.description = description
        self.img = image
        self.img_en = img_en
        self.switch_active = switch_active
        self.price_findate = price_findate
        self.type_product = type_product

        self.price_crypto = price_crypto or 0.
        self.currency_crypto = currency_crypto or 'USDT'

        if discount_percent is not None and discount_findate is not None:
            self.discount = Discount(
                percent=discount_percent, findate=discount_findate)
        else:
            self.discount = None


class Transactions(BaseModel):
    """(deprecated)"""
    id: int
    user_id: int
    code: str
    link: str | None
    sum: float
    currency: str
    status: str
    payment_date: datetime | None
    name: str
    duration_days: int
    type_product: PRODUCT_TYPE


class Purchase:
    """(deprecated)"""

    def __init__(
        self,
        user_id: int | None,
        price_id: int | None = None,
        price_name: str | None = None,
        type_product: str | None = None,
        sum: float | None = None,
        tariff_price: float | None = None,
        currency: str | None = None,
        duration: int | None = None,
        payment_date: datetime | None = None,
        create_date: datetime | None = None,

    ):
        self.user_id = user_id
        self.price_id = price_id
        self.price_name = price_name
        self.type_product = type_product
        self.sum = sum
        self.tariff_price = tariff_price
        self.currency = currency
        self.duration_days = duration
        self.payment_date = payment_date
        self.create_date = create_date


class UserInfo(BaseModel):
    id: int
    tg_id: int
    tg_username: Optional[str]
    nickname: Optional[str]
    refer_id: Optional[int]
    refer_sum: int
    ban: bool
    registration_dt: datetime
    uses_count: Optional[int]
    block: bool = False


class RefUser(BaseModel):
    id: int
    tgId: int
    tgUsername: Optional[str]
    refsCount: int


class Client(BaseModel):
    user: UserInfo | None = None


class CalculatorStats(BaseModel):
    currency: str
    profit: float
    tp_count: float
    sl_count: float
    all_stats_count: int
    saved_stats_count: int
    max_profit: float
    min_loss: float


class Worker(BaseModel):
    id: int
    tg_id: int
    username: str
    role: ROLE_TYPE


class PostDetails(BaseModel):
    name: str
    open_price: float
    stop_loss: float
    ticker: str


class Post(BaseModel):
    id: int | None = None
    content: str = ''
    mes_type: str = 'text'
    direct: str = 'Всем'
    media: str | None = None
    date_time: datetime | None = None
    details: PostDetails | None = None


class Text(BaseModel):
    id: int
    name: str
    message: str
    message_type: str
    media_id: str | None
    media_id_en: str | None


class TaskMessage(BaseModel):
    type_message: str = 'text'
    text: str = 'text'
    media_id: str | None = None


class Task(BaseModel):
    id: int | None = None
    type_task: str = 'send_message'
    user_id: int | None = None
    date_action: datetime | None = None
    message: TaskMessage | None = None
    active: int = 1


class UserCalcSettings(BaseModel):
    user_id: int
    deposit: float | None
    risk: tuple[float, bool] | None
    currency: str | None
    market: MARKETS_TYPE
    tp_ratio: list[float]
    split_values: list[float] | None
    trading_style: str | None
    round_count: int | None
    day_risk: tuple[float, bool] | None
    is_updating_deposit: bool
    trading_type: TRADING_TYPE
    is_from_deposit: bool


class ForexInfo(BaseModel):
    pair: tuple[str, str]
    price: float
    cross_prices: dict[str, float]


class CalcTrailingStop(BaseModel):
    value: float
    createdAt: str


class CalcActiveInfo(BaseModel):
    trailingStopCount: Optional[float]
    autoStop: Optional[bool]
    autoTake: Optional[float]
    chMesIds: Optional[str]
    exchange: EXCHANGE_TYPE = 'BYBIT'


class Calculation(BaseModel):
    id: int = 0
    userId: int

    profit: float | None = None
    inStat: bool = False
    statDt: Optional[str] | None = None

    market: MARKETS_TYPE
    tradingType: TRADING_TYPE
    isFromDeposit: bool
    tradingStyle: str | None
    roundCount: int | None = None

    currency: str
    deposit: float
    riskValue: float
    openPrice: float
    stopLoss: float
    newStop: Optional[float] = None

    isOpenPriceChanged: Optional[bool] = False

    tpRatio: list[float]
    splitValues: list[float] | None

    forexInfo: ForexInfo | None = None
    tool: Optional[str] = None

    status: CALC_STATUS_TYPE = 'WAIT'
    description: Optional[str] = None
    photo: Optional[str] = None
    comment: Optional[str] = None
    openedList: bool = False

    TrailingStops: Optional[list[CalcTrailingStop]] = None
    ActiveCalc: Optional[CalcActiveInfo] = None

    createdAt: Optional[str] = None
    dealAt: Optional[str] = None
    cancelAt: Optional[str] = None


class CalculationResult(BaseModel):
    count_bet: float
    value_bet: float

    tp_count: int
    tp_values: list[float]
    profit_values: list[float]
    profit_rate_values: Optional[list[float]] = None

    exchange: Optional[str] = None
    fee: Optional[float] = None


class UnfinishedCalculation(BaseModel):
    id: int
    user_id: int
    last_values: list[str]

    deposit: Optional[float] = None
    currency: Optional[str] = None

    open_price: Optional[float] = None
    tool: Optional[str] = None
    forex: Optional[ForexInfo] = None
    trading_style: Optional[str] = None
    risk_value: Optional[float] = None
    is_risk_percent: Optional[bool] = None
    update_risk_rate: Optional[float] = None


class Exchange(BaseModel):
    id: int
    name: str

    maker_fee: float
    taker_fee: float
    fees: list[tuple[str, float, float]]


class TickerInfo(BaseModel):
    turnover24h: float
    percent24h: float
    indexPrice: float
    updatedAt: str


class SentMessages(BaseModel):
    chIds: list[str]
    mesIds: list[str]
    langs: list[Literal['ru', 'en']]


class UserNotification(SentMessages):
    firstLang: str
    num: int


class UserCalcNot(BaseModel):
    userId: int
    type: Literal['cancel', 'tr_stop']
    tool: str
    chId: str
    mesId: str
    trStop: tuple[float | Literal['breakeven'], float] | None = None


class CalcSentMessages(BaseModel):
    mesNum: Optional[int] = None
    messages: Optional[dict] = None
    date: str


class SendCalc(BaseModel):
    id: int
    calcId: int
    sent: bool
    withoutStop: bool
    isPreStop: bool
    tradingStyle: Optional[str]
    time: Optional[str]
    isVote: bool
    createdAt: str
    messages: Optional[SentMessages] = None


class SendCalcWithCalc(SendCalc):
    calculation: Calculation


class LiveDeal(BaseModel):
    tool: str
    takeProfit: Optional[float]
    takeProfitRatio: Optional[float]
    messages: Optional[SentMessages]
    indexPrice: Optional[float]
    openPrice: float
    stopLoss: float
    TrailingStops: Optional[list[CalcTrailingStop]] = None


class LiveWaitCancel(BaseModel):
    tool: str
    messages: Optional[SentMessages]


class LiveFinish(LiveWaitCancel):
    valueCount: float


class LiveToUpdate(BaseModel):
    calc: Calculation
    sendData: SendCalc
    indexPrice: Optional[float]
    percent24h: Optional[float]


class Live(BaseModel):
    wait: list[LiveWaitCancel]
    canceled: list[LiveWaitCancel]
    finished: list[LiveFinish]
    deal: list[LiveDeal]
    toUpdate: list[LiveToUpdate]
    isNewMes: bool
    messages: Optional[SentMessages]

    monthProfit: float
    monthValueCount: float
    todayProfit: Optional[float]
    todayValueCount: Optional[float]


class AdvancedSettings(BaseModel):
    userId: int
    autoOpen: bool
    autoStop: bool
    autoTake: Optional[float]
    trailingStop: Optional[float]
    cancelMinutes: Optional[float]


class UserSmall(BaseModel):
    id: int
    tgId: int
    tgUsername: Optional[str]
    username: Optional[str]


class SubscribeInfo(BaseModel):
    id: int
    active: bool
    finishDt: Optional[str]
    productType: PRODUCT_TYPE
    user: UserSmall


class GetAllSubscribes(BaseModel):
    data: list[SubscribeInfo]
    count: int


class MinUser(BaseModel):
    id: int
    tgId: int
    tgUsername: Optional[str]


class ActiveStats(BaseModel):
    longCount: int
    shortCount: int
    profitCount: float


class UserActiveStats(BaseModel):
    user: MinUser
    data: ActiveStats


class AdminCalcNot(BaseModel):
    userIds: list[int]
    userName: str
    calc: Calculation
    userTgId: int
    userStats: ActiveStats


class Mean(BaseModel):
    tool: str
    exchange: str
    type: str
    description: str | None
    photo: str | None


class CalcChannelNotification(BaseModel):
    calcId: int
    tool: str
    chIds: list[str]
    mesIds: list[str]
    langs: list[LANGUAGES_TYPE]


class Poll(BaseModel):
    title: str
    ans: Optional[list[str]] = None
    rightAns: Optional[str] = None
