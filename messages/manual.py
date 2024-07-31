from common.utils import get_lang
from models import MANUAL_TYPE


def msg_manual(user_id: int, type: MANUAL_TYPE):
    lang = get_lang(user_id)

    if type == 'calc':
        if lang == 'ru':
            return """Для чего калькулятор?

Если Вы когда-нибудь слышали слово "риск-менеджмент", то это именно тот самый инструмент, позволяющий управлять капиталом. 

Калькулятор для расчета ваших убытков и прибыли.

 Работает элементарно.

Вписываете свой депозит, сумму или процент от капитала, который готовы "потерять" в сделке, а калькулятор высчитывает количество монет/акций/лотов (в зависимости от рынка) для покупки.

Вот пример.

У меня есть баланс в 10 000 долларов.

1 условие:

Я хочу купить Биткоин по цене 66 000 долларов.

2 условие:

Моя цена стоп-лосс пусть будет 65850 (вот так я решил, что ниже этой цены упасть не дам)

3 условие:

Я готов от 10 000 USDT депозита зафиксировать убыток в 100 USDT (стоп-лосс)

Вопрос, сколько нужно купить монет, чтобы в убыточном случае депозит остался в размере 9900 USDT?

4 условие:

Ввожу данные в калькулятор и идет автоматически расчет, где мне нужно по цене 66 000 купить 0.7909 монет, а при цене 65873.56 выставить свой стоп-лосс (и тогда потеря суммы будет не более 100 USDT)

А при цене 66379.32 прибыль со сделки уже составит +300 USDT

Итог: вот как работают профессионалы, от сделки до сделки.
Трейдинг - это не казино, а расчеты и системный подход.

Информация дополняется."""
        else:
            return """<b>What is the calculator intended for? </b>

If you've ever heard the term “risk management”, this is the very tool that allows you to manage your capital.

A calculator is designed to calculate your <b>losses and profits</b>.

 It functionality is very simple.

You enter your deposit, the amount or percentage of capital you are willing to “lose” in a trade, and <b>the calculator</b> estimates the <b>number</b> of coins/shares/lots (depending on the market) to buy.

<b>Here's an example. </b>

I have a balance of $10,000.

<b>1 condition: </b>

I want to buy Bitcoin at a price of $66,000.

<b>2 condition: </b>

Let my stop loss price be at 65850 (this way I have decided that I will not let it fall below this price)

<b>3 condition: </b>

I am ready to fix a loss (stop loss) of <b>100 USDT</b> from <b>10 000 USDT</b> deposit

Question: how many coins should I buy so that I can keep a deposit of 9900 USDT in the losing scenario?

<b>4 condition: </b>

I enter the data into the calculator and it automatically gives me the calculation. I need to buy 0.7909 coins at the price of 66 000, and set my stop loss at the price of 65873.56 (and then the loss will not exceed 100 USDT).

And at the price of <b>66379.32</b>, the profit from the trade will be <b>+300 USDT</b>

Bottom line: this is how professionals work, from trade to trade.
Trading is not a casino, it's calculations and systematic approach.

The information is being supplemented."""

    elif type == 'settings':
        if lang == 'ru':
            return """""Настроить торговлю"

<b>1. Изменить торговлю</b>

Впишите депозит, изменяйте, а система подстроится.

<b>2. Включить обновление депозита</b>

Сохраняя сделку, сумма депозита изменяется, а новый расчет происходит уже с <b>обновленным</b> депозитом

<b>3. Изменить валюту</b>

Изменяете валюту и получаете расчеты.

<b>4. Процент риска </b>

Еще перед входом в сделку, <b>трейдер</b> должен верно <b>рассчитать</b> <b>объем</b> покупки/продажи инструмента

Выберите <b>% риска на сделку</b> от депозита и получайте расчеты, заведомо зная, что выше желаемой суммы убытка не ожидается.

<b>5. Риск на день</b>

Прописывая % риска на день и выходя за "рамки", система будет об этом напоминать. Иногда эмоции могут брать выше, а это полезный функционал.

<b>6. Округление </b>

Округление данных идет с учетом ваших приоритетов во время торговли, нужно помнить, что есть инструменты с ценой в 5 нулей после запятой.

<b>7. Деление профита </b>

Из сделки можно выйти  3-4-5 или более к 1 или выходить <b>"частями"</b>, потому как прибыльные сделки можно  держать и более, разбив на <b>"части"</b>"""
        else:
            return """Configure trading

<b>1. Change deposit</b>
Enter the deposit, change it and the system will adjust to your value.

<b>2. Enable deposit update</b>
By saving the trade, the deposit amount changes, and the new calculation takes place already with the updated deposit

<b>3. Change currency</b>
Changing the currency and getting the calculations.

<b>4. Risk percent</b>
Choose the % of risk per transaction from the deposit and get calculations knowing that no loss is expected above the desired amount.

<b>5. Daily risk</b>
By specifying the % of daily risk, and then going beyond the “limits”, the system will remind you about it. Sometimes emotions can get out of your control, so this is a useful feature.

<b>6. Rounding </b>
Rounding of data is based on your trading priorities. You need to remember that there are tools with a price of 5 decimal places.

<b>7. Profit division </b>
You can exit a trade 3-4-5 or more to 1 or exit in “portions”, because profitable trades can be kept more, divided into “portions”."""

    elif type == 'exchange':
        if lang == 'ru':
            return """<b>Биржа</b>

Выберите <b>биржу</b>, а также статус, а система будет рассчитывать комиссии за покупки/продажи и заранее прописывать перед покупкой

<b>Комиссии</b> тоже должны учитываться в риск-менеджменте <b>трейдера</b>"""
        else:
            return """<b>Exchange</b>

Select <b>the exchange</b> and the level and the system will calculate the fee for buys/sells and prescript it in advance before making a deal

<b>Fee</b> should be considered in the <b>trader's</b> risk management too"""

    elif type == 'trading_type':
        if lang == 'ru':
            return """<b>Спотовый</b>

У трейдера <b>точный</b> депозит, без кредитных плеч. И расчет идет на эту сумму, не более.

<b>Маржинальный</b>

Трейдер может использовать кредитные плечи, предоставляемые биржей, для покупки/продажи большего объема"""
        else:
            return """<b>Spot </b>

The trader has an exact deposit, without leverage. And the calculation is made based on this amount, no more.

<b>Margin</b>

The trader can use the leverage provided by the exchange to buy/sell more volume"""

    elif type == 'trading_style':
        if lang == 'ru':
            return """Выберите стиль торговли или напишите свой

<b>Пробой</b> - когда цена пробивает уровень и идет выше

<b>Отбой</b> - цена подошла к уровню и отбивается от него в направлении трейдера

<b>Ложный</b> - обманное движение крупного игрока для набора большей позиции, а для <b>трейдера</b> - это стиль торговли

<b>Скользящие</b> <b>средние</b> - один из самых популярных стилей

<b>High/low </b>- как правило, чаще всего этот стиль используют трейдеры на средний срок, входя/выходя на пиковых значения

<b>Выбирайте, меняйте, управляйте</b> и это будет сохраняться в статистику для отслеживания результатов автоматически за вас."""
        else:
            return """Select a trading style or write your own

<b>Breakout</b>: when the price breaks through the level and goes higher

<b>Bounce</b>: the price has approached the level and bounces off it in the trader's direction

<b>Fakeout</b> (false breakout): a deceptive move by a major player to gain a larger position, but for the trader, it is a trading style.

<b>Moving average</b>: one of the most popular styles.

<b>High/low</b>: generally, this style is used by traders for medium-term trading, entering/exiting at peak values

<b>Select, change, manage</b> and it will be saved in the stats to track results automatically for you."""
