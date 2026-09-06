import sys

sys.path.insert(
    0,
    r"C:\Users\test4\atlas-omega-work\atlas-omega\app\src"
)

from omega_analytics.backtest import BacktestEngine
from omega_analytics.replay import ReplayEngine


backtest = BacktestEngine()
replay = ReplayEngine()


trades = []


trades.append(
    backtest.simulate_trade(
        symbol="ROSN",
        strategy="ROSN_HEDGE_V3",
        entry_price=319,
        exit_price=320.5,
        quantity=10,
        stop_loss=317.5,
        take_profit=320.5,
    )
)


trades.append(
    backtest.simulate_trade(
        symbol="ROSN",
        strategy="ROSN_HEDGE_V3",
        entry_price=318,
        exit_price=317,
        quantity=10,
        stop_loss=317,
        take_profit=320,
    )
)


trades.append(
    backtest.simulate_trade(
        symbol="ROSN",
        strategy="ROSN_HEDGE_V3",
        entry_price=310,
        exit_price=313,
        quantity=10,
        stop_loss=308,
        take_profit=313,
    )
)


report = replay.build_report(
    strategy="ROSN_HEDGE_V3",
    trades=trades,
)


print(report)


assert report.trades == 3
assert report.wins == 2
assert report.losses == 1

print("REPLAY TEST OK")