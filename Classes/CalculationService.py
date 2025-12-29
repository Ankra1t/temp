from models import Calculation, CalculationResult


class CalculationService():
    def __init__(self) -> None:
        pass

    def get_count_value_bet(self, calc: Calculation, lot=pow(10, 5)):
        spot_rate = 1.

        diff_op_sl = calc.openPrice - calc.stopLoss

        if calc.market == 'forex' and calc.forexInfo is not None:
            value_bet = calc.riskValue / abs(diff_op_sl)
            count_bet = value_bet / lot

            if calc.currency == calc.forexInfo.pair[1]:
                value_bet *= calc.openPrice
            elif calc.currency == calc.forexInfo.pair[0]:
                count_bet *= calc.stopLoss
                value_bet = count_bet * lot
            else:
                prices = calc.forexInfo.cross_prices

                BASExxx = f'{calc.currency}/{calc.forexInfo.pair[1]}'
                yyyBASE = f'{calc.forexInfo.pair[0]}/{calc.currency}'

                count_bet *= prices.get(BASExxx, 1)
                value_bet = count_bet * lot * prices.get(yyyBASE, 1)
        else:
            count_bet = calc.riskValue / abs(diff_op_sl)
            value_bet = count_bet * calc.openPrice

        if calc.tradingType == 'spot' and value_bet > calc.deposit:
            spot_rate = calc.deposit / value_bet

            count_bet *= spot_rate
            value_bet = calc.deposit

        return count_bet, value_bet, spot_rate

    def get_result(self, calc: Calculation):
        count_bet, value_bet, _ = self.get_count_value_bet(calc)

        fee = value_bet
        value_bet += fee

        tp_values: list[float] = []
        profit_values: list[float] = []
        profit_rate_values: list[float] | None = None

        tp_count = len(calc.tpRatio)

        is_splitting = (
            calc.splitValues is not None and
            len(calc.splitValues) != 0 and
            len(calc.splitValues) == tp_count
        )

        if is_splitting:
            profit_rate_values = []

        for i in range(tp_count):
            tp_ratio_i = calc.tpRatio[i]

            diff_op_sl = calc.openPrice - calc.stopLoss
            tp_i = max(
                calc.openPrice + diff_op_sl * tp_ratio_i,
                0
            )
            tp_values.append(tp_i)

            profit_rate_i = 1
            if is_splitting:
                profit_rate_i = calc.splitValues[i] * 0.01  # type: ignore
                profit_rate_values.append(profit_rate_i)  # type: ignore

            profit_i = abs(calc.openPrice - tp_i) * count_bet * profit_rate_i

            if calc.market == 'forex' and calc.forexInfo is not None:
                profit_i *= pow(10, 5)
                if calc.forexInfo.pair[0] == calc.currency:
                    profit_i /= calc.stopLoss
                elif calc.forexInfo.pair[1] != calc.currency:
                    profit_i /= calc.forexInfo.cross_prices.get(
                        f'{calc.currency}/{calc.forexInfo.pair[1]}', 1
                    )

            profit_values.append(profit_i - 2 * fee)

        return CalculationResult(
            count_bet=count_bet,
            value_bet=value_bet,

            tp_count=tp_count,
            profit_rate_values=profit_rate_values,
            profit_values=profit_values,
            tp_values=tp_values,

            exchange=None,
            fee=fee or None,
        )
