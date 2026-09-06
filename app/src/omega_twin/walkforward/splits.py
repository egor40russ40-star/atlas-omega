from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass(frozen=True, slots=True)
class WalkForwardFold:
    fold_no: int
    train_start: datetime
    train_end: datetime
    validation_start: datetime
    validation_end: datetime
    purge_seconds: int
    embargo_seconds: int

def generate_folds(
    *,
    start: datetime,
    end: datetime,
    train_days: int,
    validation_days: int,
    step_days: int,
    purge_seconds: int = 0,
    embargo_seconds: int = 0,
) -> tuple[WalkForwardFold,...]:
    folds=[]
    cursor=start
    n=1
    while True:
        train_start=cursor
        train_end=train_start+timedelta(days=train_days)
        validation_start=train_end+timedelta(seconds=embargo_seconds)
        validation_end=validation_start+timedelta(days=validation_days)
        if validation_end>end:
            break
        folds.append(WalkForwardFold(
            n,train_start,train_end,validation_start,validation_end,
            purge_seconds,embargo_seconds
        ))
        cursor += timedelta(days=step_days)
        n+=1
    return tuple(folds)

def in_purged_train_window(
    event_start: datetime,
    event_end: datetime,
    fold: WalkForwardFold,
) -> bool:
    purge_boundary = fold.train_end - timedelta(seconds=fold.purge_seconds)
    return event_start >= fold.train_start and event_end <= purge_boundary
