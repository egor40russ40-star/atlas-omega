from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from .model import LedgerTransaction, LedgerPosting
from .invariants import validate_balanced

def _p(account: str, amount: Decimal, currency: str, broker_account_id: str | None = None) -> LedgerPosting:
    return LedgerPosting(
        posting_id=uuid4(),
        ledger_account=account,
        currency=currency,
        amount=amount,
        broker_account_id=broker_account_id,
    )

def make_external_deposit(
    amount: Decimal,
    currency: str,
    broker_account_id: str,
    broker_operation_id: str | None = None,
) -> LedgerTransaction:
    if amount <= 0:
        raise ValueError("deposit amount must be positive")
    tx = LedgerTransaction(
        transaction_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        event_type="DEPOSIT",
        source_type="BROKER",
        source_id=broker_account_id,
        broker_operation_id=broker_operation_id,
        description_ru="Внешнее пополнение брокерского счёта",
        postings=(
            _p("DEPOSIT_CONTROL", -amount, currency, broker_account_id),
            _p("CASH", amount, currency, broker_account_id),
        ),
    )
    validate_balanced(tx)
    return tx

def make_withdrawal(
    amount: Decimal,
    currency: str,
    broker_account_id: str,
    broker_operation_id: str | None = None,
) -> LedgerTransaction:
    if amount <= 0:
        raise ValueError("withdrawal amount must be positive")
    tx = LedgerTransaction(
        transaction_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        event_type="WITHDRAWAL",
        source_type="BROKER",
        source_id=broker_account_id,
        broker_operation_id=broker_operation_id,
        description_ru="Вывод средств с брокерского счёта",
        postings=(
            _p("CASH", -amount, currency, broker_account_id),
            _p("WITHDRAWAL_CONTROL", amount, currency, broker_account_id),
        ),
    )
    validate_balanced(tx)
    return tx

def make_commission(
    amount: Decimal,
    currency: str,
    broker_account_id: str,
    broker_operation_id: str | None = None,
) -> LedgerTransaction:
    if amount <= 0:
        raise ValueError("commission amount must be positive")
    tx = LedgerTransaction(
        transaction_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        event_type="COMMISSION",
        source_type="BROKER",
        source_id=broker_account_id,
        broker_operation_id=broker_operation_id,
        description_ru="Комиссия брокера",
        postings=(
            _p("CASH", -amount, currency, broker_account_id),
            _p("COMMISSION_EXPENSE", amount, currency, broker_account_id),
        ),
    )
    validate_balanced(tx)
    return tx

def make_unclassified_balance_change(
    delta: Decimal,
    currency: str,
    broker_account_id: str,
) -> LedgerTransaction:
    if delta == 0:
        raise ValueError("delta must be non-zero")
    tx = LedgerTransaction(
        transaction_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        event_type="UNCLASSIFIED_BALANCE_CHANGE",
        source_type="RECONCILIATION",
        source_id=broker_account_id,
        broker_operation_id=None,
        description_ru="Необъяснённое изменение баланса — временно помещено в suspense",
        postings=(
            _p("SUSPENSE_CONTROL", -delta, currency, broker_account_id),
            _p("CASH", delta, currency, broker_account_id),
        ),
    )
    validate_balanced(tx)
    return tx
