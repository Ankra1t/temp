import uuid

from yookassa import Configuration, Payment

Configuration.account_id = 362894
Configuration.secret_key = 'test_zOXAOR8Is_d0AU_ZmJwQz7AypCXjuE16kIxw20zS-AU'


def create_payment():
    payment = Payment.create(
        {
            "amount": {
                "value": "100.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://www.example.com/return_url"
            },
            "capture": True,
            "description": "Заказ №1"
        },
        uuid.uuid4()
    )

    print(payment.status)
