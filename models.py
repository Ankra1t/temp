from pydantic import BaseModel
from typing import Literal, Union, Optional
from datetime import datetime


MARKETS_TYPE = Literal['crypto', 'paper', 'forex', 'RF', 'USA']
PRODUCT_TYPE = Literal['signals', 'calc', 'calc_signals']


class Invoice(BaseModel):
    """Структура чека"""
    invoice_id: int
    status: str
    asset: str
    amount: Union[int, float]
    pay_url: str
    description: Optional[str] = None
    allow_comments: bool
    allow_anonymous: bool


class InvoiceBBanker(BaseModel):
    invoice_id: Optional[int] = None
    status: Optional[str] = None
    asset: Optional[str] = None
    amount: Optional[Union[int, float]] = None
    pay_url: Optional[str] = None
    description: Optional[str] = None


class Update(BaseModel):
    update_id: int
    update_type: str
    request_date: datetime
    payload: Invoice


class UpdateBBanker(BaseModel):
    payload: InvoiceBBanker | None = None


class Subscribe(BaseModel):
    id: int
    user_id: int
    finish_dt: datetime
    product_type: PRODUCT_TYPE
    active: bool
    transactions_payed_id: Optional[int] = None


class User:
    def __init__(self):
        self.id: int | None = None
        self.username: str | None = None
        self.subscribe_days: int | None = None
        self.subscribe: Subscribe | None = None


class Discount(BaseModel):
    percent: float
    findate: datetime


class Price:
    type_product: PRODUCT_TYPE

    def __init__(
        self,
        name: str,
        duration: int,
        price: int,
        currency: str,
        switch_active: int,
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
    username: str
    refer: int
    ban: int
    registration_dt: datetime
    uses_count: Optional[int]


class Client(BaseModel):
    user: UserInfo | None = None


class CalculatorStats(BaseModel):
    currency: str
    profit: float
    tp_count: int
    sl_count: float
    all_stats_count: int
    saved_stats_count: int
    max_profit: float
    min_loss: float

# class Client(BaseModel):
#     user: UserInfo | None = None
#     subscribes: Optional[list[Subscribe], Subscribe, None] = None


class Worker(BaseModel):
    id: int
    tg_id: int
    username: str
    role: int


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
    media_id: str
    media_id_en: str | None


class Forex(BaseModel):
    id: int
    pair: str
    price: float
    help_pair: str | None


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
    tp_ratio: list[int]
    split_values: list[float] | None
    trading_style: str | None
    round_count: int | None
    day_risk: tuple[float, bool] | None
    is_updating_deposit: bool


class ForexInfo(BaseModel):
    pair: tuple[str, str]
    price: float
    cross_prices: dict[str, float]


class Calculation(BaseModel):
    id: int = 0
    profit: float | None = None
    in_stat: bool = False
    stat_dt: datetime | None = None
    user_id: int

    deposit: float
    risk_value: float
    open_price: float
    stop_loss: float
    currency: str
    trading_style: str | None
    market: MARKETS_TYPE
    tp_ratio: list[int]
    round_count: int | None = None
    split_values: list[float] | None

    forex_info: ForexInfo | None = None
    tool: Optional[str] = None


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

