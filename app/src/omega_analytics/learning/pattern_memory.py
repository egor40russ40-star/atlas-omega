from dataclasses import dataclass, field


@dataclass
class PatternRecord:
    symbol: str
    strategy: str
    pattern: str

    trades: int = 0
    wins: int = 0
    losses: int = 0

    total_r: float = 0.0

    @property
    def win_rate(self):
        if self.trades == 0:
            return 0.0

        return round(
            self.wins / self.trades * 100,
            2
        )

    @property
    def average_r(self):
        if self.trades == 0:
            return 0.0

        return round(
            self.total_r / self.trades,
            2
        )


class PatternMemory:
    """
    Память эффективности торговых паттернов.
    """

    def __init__(self):
        self.records = {}

    def update(
        self,
        *,
        symbol: str,
        strategy: str,
        pattern: str,
        result: str,
        r_multiple: float,
    ):

        key = (
            symbol,
            strategy,
            pattern,
        )

        if key not in self.records:
            self.records[key] = PatternRecord(
                symbol=symbol,
                strategy=strategy,
                pattern=pattern,
            )

        record = self.records[key]

        record.trades += 1
        record.total_r += r_multiple

        if result == "WIN":
            record.wins += 1

        elif result == "LOSS":
            record.losses += 1


        return record

    def get(
        self,
        symbol,
        strategy,
        pattern,
    ):

        return self.records.get(
            (
                symbol,
                strategy,
                pattern,
            )
        )