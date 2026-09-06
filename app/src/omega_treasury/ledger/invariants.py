from __future__ import annotations
from collections import defaultdict
from decimal import Decimal
from .model import LedgerTransaction

def validate_balanced(tx: LedgerTransaction) -> None:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    if len(tx.postings) < 2:
        raise ValueError("TREASURY_LEDGER_UNBALANCED")
    for p in tx.postings:
        totals[p.currency] += p.amount
    bad = {ccy: total for ccy, total in totals.items() if total != Decimal("0")}
    if bad:
        raise ValueError(f"TREASURY_LEDGER_UNBALANCED:{bad}")

def transaction_is_balanced(tx: LedgerTransaction) -> bool:
    try:
        validate_balanced(tx)
        return True
    except ValueError:
        return False
