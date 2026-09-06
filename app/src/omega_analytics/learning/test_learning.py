import sys

sys.path.insert(
    0,
    r"C:\Users\test4\atlas-omega-work\atlas-omega\app\src"
)
from omega_analytics.learning import PatternMemory


memory = PatternMemory()


for i in range(7):
    memory.update(
        symbol="ROSN",
        strategy="ROSN_HEDGE_V3",
        pattern="support_retest",
        result="WIN",
        r_multiple=1.4,
    )


for i in range(3):
    memory.update(
        symbol="ROSN",
        strategy="ROSN_HEDGE_V3",
        pattern="support_retest",
        result="LOSS",
        r_multiple=-1.0,
    )


record = memory.get(
    "ROSN",
    "ROSN_HEDGE_V3",
    "support_retest",
)


print(record)
print(
    "WIN RATE:",
    record.win_rate
)

print(
    "AVG R:",
    record.average_r
)


assert record.trades == 10
assert record.wins == 7
assert record.losses == 3

print("LEARNING TEST OK")