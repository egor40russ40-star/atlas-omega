from __future__ import annotations
from datetime import datetime, timedelta
from uuid import uuid4
import secrets
from omega_commander.domain.models import ConfirmationChallenge
from omega_commander.commands.hash import command_hash

SUMMARIES = {
    "ENTER_SAFE":"Перевести систему в SAFE",
    "EMERGENCY_STOP":"Активировать аварийную остановку торговли",
    "RESTART_CRITICAL_SERVICE":"Перезапустить критический сервис",
    "RESUME_TRADING":"Возобновить торговый контур",
}

CONSEQUENCES = {
    "ENTER_SAFE":(
        "Новые торговые входы будут запрещены.",
        "Потребуется последующая проверка READY перед LIVE.",
    ),
    "EMERGENCY_STOP":(
        "Новые торговые действия будут заблокированы.",
        "Потребуется устранить причину и пройти восстановление.",
    ),
    "RESTART_CRITICAL_SERVICE":(
        "Критический модуль будет кратковременно недоступен.",
        "Команда разрешена только в SAFE/RECOVERY.",
    ),
    "RESUME_TRADING":(
        "Новые торговые входы снова смогут проходить полный Capital/Risk/Safety путь.",
        "Команда разрешена только после READY и при выключенном Kill Switch.",
    ),
}

class ConfirmationManager:
    def __init__(self, ttl_seconds: int = 30) -> None:
        self.ttl_seconds=ttl_seconds
        self._challenges={}

    def create(self, command, *, now: datetime) -> ConfirmationChallenge:
        c=ConfirmationChallenge(
            uuid4(),command.command_id,command_hash(command),
            now,now+timedelta(seconds=self.ttl_seconds),
            secrets.token_hex(16),
            SUMMARIES.get(command.command_type.value,command.command_type.value),
            CONSEQUENCES.get(command.command_type.value,()),
        )
        self._challenges[c.confirmation_id]=c
        return c

    def validate(self, confirmation_id, command, *, now: datetime) -> list[str]:
        c=self._challenges.get(confirmation_id)
        if c is None:
            return ["CMD_CONFIRMATION_REQUIRED"]
        reasons=[]
        if c.expires_at <= now:
            reasons.append("CMD_CONFIRMATION_EXPIRED")
        if c.command_id != command.command_id or c.command_hash != command_hash(command):
            reasons.append("CMD_CONFIRMATION_HASH_MISMATCH")
        return sorted(set(reasons))
