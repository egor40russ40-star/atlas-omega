from dataclasses import dataclass


@dataclass
class TradeResult:
    symbol: str
    strategy: str

    entry_price: float
    exit_price: float

    quantity: int

    stop_loss: float | None = None
    take_profit: float | None = None

    pnl: float = 0.0
    r_multiple: float = 0.0

    status: str = "UNKNOWN"


class TradeAnalyzer:
    """
    Анализатор результата сделки.
    """

    def analyze(
        self,
        *,
        symbol: str,
        strategy: str,
        entry_price: float,
        exit_price: float,
        quantity: int,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> TradeResult:

        pnl = (
            exit_price - entry_price
        ) * quantity


        risk = None

        if stop_loss is not None:
            risk = abs(entry_price - stop_loss)


        if risk and risk > 0:
            r_multiple = (
                (exit_price - entry_price)
                / risk
            )
        else:
            r_multiple = 0.0


        if pnl > 0:
            status = "WIN"
        elif pnl < 0:
            status = "LOSS"
        else:
            status = "BREAKEVEN"


        return TradeResult(
            symbol=symbol,
            strategy=strategy,

            entry_price=entry_price,
            exit_price=exit_price,

            quantity=quantity,

            stop_loss=stop_loss,
            take_profit=take_profit,

            pnl=pnl,
            r_multiple=round(r_multiple, 2),

            status=status,
        )