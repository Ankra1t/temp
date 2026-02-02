from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    Message as _Message,
    User as _User,
    CallbackQuery as _CallbackQuery,
)
from telebot.states.asyncio.context import StateContext as _StateContext
from telebot.asyncio_storage.base_storage import StateDataContext as _StateDataContext
from telebot.asyncio_filters import AdvancedCustomFilter
from telebot.states import State
from telebot.states import resolve_context

from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

BASE_VALUE_TYPE = Literal["deposit", "risk", "currency"]
SORT_BY_TYPE = Literal["new", "old"]

TRADING_TYPE = Literal["margin", "spot", "future"]
MARKETS_TYPE = Literal["crypto", "paper", "forex", "RF", "USA"]
EXCHANGE_TYPE = Literal["BYBIT", "BINANCE"]
PRODUCT_TYPE = Literal["signals", "calc", "calc_signals", "active_calc"]
CALC_STATUS_TYPE = Literal["WAIT", "CANCEL", "FINISH", "DEAL"]

MANUAL_TYPE = Literal["settings", "exchange",
                      "trading_type", "trading_style", "calc"]

# Языки вывода
LANGUAGES_TYPE = Literal["ru", "en", "uz", "tr"]
LANGUAGES: tuple[LANGUAGES_TYPE, ...] = ("ru", "en", "uz", "tr")

STYLES = {
    "Пробой": "пробой уровня",
    "Отбой": "отбой от уровня",
    "Ложные": "ложные пробои",
    "Скользящие": "скользящие средние",
    "High/low": "торговля на high/low",
    "В канале": "в канале",
}


class StateFilter(AdvancedCustomFilter):
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    key = "state"

    async def check(self, message, text):
        if self.bot.bot_id is None or self.bot.current_states is None:
            return

        chat_id, user_id, business_connection_id, bot_id, message_thread_id = (
            resolve_context(message, self.bot.bot_id)
        )

        if chat_id is None:
            chat_id = user_id  # Может измениться в будущем

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
            business_connection_id=business_connection_id,
            bot_id=bot_id,
            message_thread_id=message_thread_id,
        )

        # ИЗМЕНЁННОЕ ПОВЕДЕНИЕ
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
    from_user: _User  # type: ignore


class CallbackQuery(_CallbackQuery):
    message: Message  # type: ignore


class User(BaseModel):
    """Пользователь кратко"""

    id: int
    tgId: int
    lang: LANGUAGES_TYPE
    role: Literal[1, 0]


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


class CalculatorStats(BaseModel):
    currency: str
    profit: float
    tp_count: float
    sl_count: float
    all_stats_count: int
    saved_stats_count: int
    max_profit: float
    min_loss: float


class PostDetails(BaseModel):
    name: str
    open_price: float
    stop_loss: float
    ticker: str


class Post(BaseModel):
    id: int | None = None
    content: str = ""
    mes_type: str = "text"
    direct: str = "Всем"
    media: str | None = None
    date_time: datetime | None = None
    details: PostDetails | None = None


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
    exchange: EXCHANGE_TYPE = "BYBIT"


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

    status: CALC_STATUS_TYPE = "WAIT"
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


class SentMessages(BaseModel):
    chIds: list[str]
    mesIds: list[str]
    langs: list[Literal["ru", "en"]]


class UserNotification(SentMessages):
    firstLang: str
    num: int


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
