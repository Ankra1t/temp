from pydantic import BaseModel
from typing import Literal, Union, Optional
from datetime import datetime


MARKETS_TYPE = Literal['crypto', 'future', 'paper', 'forex']


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


class Subscribe:
    def __init__(
        self,
        tg_user_id: int,
        finish_dt: datetime,
        active: int,
        id: int | None = None,
        type: str | None = None,
        prices_id: int | None = None,
        transactions_payed_id: int | None = None,
        type_product: str | None = None,
        gift_admin: int | None = None,
        user_id: int | None = None
    ):
        self.id = id
        self.tg_user_id = tg_user_id
        self.finish_dt = finish_dt
        self.type = type
        self.active = active
        self.prices_id = prices_id
        self.transactions_payed_id = transactions_payed_id
        self.type_product = type_product
        self.gift_admin = gift_admin
        self.user_id = user_id


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
    def __init__(
        self,
        name: str,
        duration: int,
        price: int,
        currency: str,
        id: int | None = None,
        image: str | None = None,
        description: str | None = None,
        discount_percent: float | None = None,
        discount_findate: datetime | None = None,
        type_product: str | None = None,
        switch_active: int | None = None,
        price_findate: datetime | None = None,
    ):
        self.id = id
        self.name = name
        self.currency = currency
        self.price = price
        self.duration_days = duration
        self.description = description
        self.img = image
        self.type_product = type_product
        self.switch_active = switch_active
        self.price_findate = price_findate

        if discount_percent is not None and discount_findate is not None:
            self.discount = Discount(
                percent=discount_percent, findate=discount_findate)
        else:
            self.discount = None


class Transactions:
    def __init__(
        self,
        user_id: int,
        id: int | None = None,
        code: str | None = None,
        link: str | None = None,
        sum: float | None = None,
        currency: str | None = None,
        price_id: int | None = None,
        status: str | None = None,
        payment_date: str | None = None,

    ):
        self.id = id
        self.user_id = user_id
        self.code = code
        self.link = link
        self.sum = sum
        self.currency = currency
        self.price_id = price_id
        self.status = status
        self.payment_date = payment_date


class Purchase:
    def __init__(
        self,
        user_id: int | None,
        price_id: int | None = None,
        price_name: str | None = None,
        type_product: str | None = None,
        real_sum: float | None = None,
        tariff_price: float | None = None,
        currency: str | None = None,
        duration: int | None = None,
        payment_date: str | None = None,
        create_date: str | None = None,

    ):
        self.user_id = user_id
        self.price_id = price_id
        self.price_name = price_name
        self.type_product = type_product
        self.real_sum = real_sum
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


class Client(BaseModel):
    user: UserInfo | None = None


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


class Future(BaseModel):
    id: int
    name: str
    step: float
    price_step: float


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


class Calculation(BaseModel):
    id: int = 0
    profit: float | None = None
    in_stat: bool = False
    user_id: int

    deposit: float
    risk_value: float
    open_price: float
    stop_loss: float
    currency: str
    trading_style: str
    market: MARKETS_TYPE
    tp_ratio: list[int]
    round_count: int | None = None
    split_values: list[float] | None
