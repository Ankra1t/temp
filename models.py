from pydantic import BaseModel
from typing import Union, Optional
from datetime import datetime


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
    ):
        self.id = id
        self.tg_user_id = tg_user_id
        self.finish_dt = finish_dt
        self.type = type
        self.active = active
        self.prices_id = prices_id
        self.transactions_payed_id = transactions_payed_id


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
        discount_findate: datetime | None = None
    ):
        self.id = id
        self.name = name
        self.currency = currency
        self.price = price
        self.duration_days = duration
        self.description = description
        self.img = image

        if discount_percent is not None and discount_findate is not None:
            self.discount = Discount(percent=discount_percent, findate=discount_findate)
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
