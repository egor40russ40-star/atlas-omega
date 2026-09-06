from __future__ import annotations
from dataclasses import replace
from omega_commander.domain.models import CommandState, CommandResult, CommandType
from omega_commander.auth.policy import authorize
from omega_commander.safety.command_guard import contextual_reasons

class CommandBus:
    def __init__(self, control_port, confirmation_manager) -> None:
        self.control=control_port
        self.confirmations=confirmation_manager
        self._results_by_key={}

    def execute(self, command, system_status, *, now, confirmation_id=None) -> CommandResult:
        existing=self._results_by_key.get(command.idempotency_key)
        if existing is not None:
            return existing

        decision=authorize(command.principal.role,command.command_type)
        before=system_status.operational_state

        if not decision.allowed:
            result=CommandResult(
                command.command_id,CommandState.DENIED,decision.reason_codes,
                "Команда запрещена.",before,before
            )
            self._results_by_key[command.idempotency_key]=result
            return result

        ctx=contextual_reasons(command,system_status)
        if ctx:
            result=CommandResult(
                command.command_id,CommandState.DENIED,tuple(ctx),
                "Команда заблокирована текущим состоянием системы.",before,before
            )
            self._results_by_key[command.idempotency_key]=result
            return result

        if decision.requires_confirmation:
            reasons=self.confirmations.validate(confirmation_id,command,now=now) if confirmation_id else ["CMD_CONFIRMATION_REQUIRED"]
            if reasons:
                # Awaiting confirmation must NOT be cached by idempotency key;
                # the same command may later be confirmed.
                return CommandResult(
                    command.command_id,CommandState.AWAITING_CONFIRMATION,tuple(reasons),
                    "Требуется отдельное подтверждение.",before,before
                )

        ct=command.command_type
        reasons=()
        if ct is CommandType.SAFE_PAUSE:
            reasons=self.control.safe_pause()
        elif ct is CommandType.ENTER_SAFE:
            reasons=self.control.enter_safe()
        elif ct is CommandType.EMERGENCY_STOP:
            reasons=self.control.emergency_stop()
        elif ct is CommandType.RESUME_TRADING:
            reasons=self.control.resume()
        elif ct in {CommandType.RESTART_NONCRITICAL_SERVICE,CommandType.RESTART_CRITICAL_SERVICE}:
            reasons=self.control.restart_service(command.target)
        elif ct is CommandType.ACK_INCIDENT:
            reasons=self.control.acknowledge_incident(str(command.params.get("incident_id","")))
        elif ct is CommandType.UPDATE_OPERATIONAL_SETTING:
            reasons=()

        after=getattr(self.control,"state",None)
        after_state=getattr(after,"operational_state",before)
        result=CommandResult(
            command.command_id,CommandState.COMPLETED,tuple(reasons),
            "Команда выполнена.",before,after_state
        )
        self._results_by_key[command.idempotency_key]=result
        return result
