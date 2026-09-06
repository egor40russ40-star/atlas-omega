from .models import BacktestTrade


class BacktestEngine:
    """
    Движок исторического моделирования сделок.
    """

    def simulate_trade(
        self,
        *,
        symbol: str,
        strategy: str,
        entry_price: float,
        exit_price: float,
        quantity: int,
        stop_loss: float,
        take_profit: float,
    ) -> BacktestTrade:

        pnl = (
            exit_price - entry_price
        ) * quantity


        risk = abs(
            entry_price - stop_loss
        ) * quantity


        if risk == 0:
            r_multiple = 0

        else:
            r_multiple = round(
                pnl / risk,
                2
            )


        if exit_price >= take_profit:
            status = "WIN"

        elif exit_price <= stop_loss:
            status = "LOSS"

        else:
            status = "OPEN"


        return BacktestTrade(
            symbol=symbol,
            strategy=strategy,

            entry_price=entry_price,
            exit_price=exit_price,

            quantity=quantity,

            stop_loss=stop_loss,
            take_profit=take_profit,

            pnl=round(pnl, 2),
            r_multiple=r_multiple,

            status=status,
        )