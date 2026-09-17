# 14. SELF-TEST, OBSERVABILITY AND AUTO-RECOVERY

Status: ARCHITECTURE ONLY
APK build: FORBIDDEN until explicit user command

## Goal

Make ATLAS Mobile diagnose its own connection/session failures and recover from transient faults automatically without hiding real security or configuration problems.

## Layered health model

Do not display one misleading ONLINE/OFFLINE flag.

Track independent layers:

1. Android network
2. Tailscale reachability
3. Gateway HTTPS
4. Gateway authentication
5. Device trust
6. NucBox reachability
7. SSH transport
8. PTY
9. tmux session
10. SFTP
11. control-plane capabilities

Example state:

NETWORK = PASS
TAILSCALE = PASS
GATEWAY = PASS
NUCBOX = PASS
SSH = DEGRADED
TMUX = UNKNOWN

The UI can then explain the actual failure.

## Startup self-test

At app launch, perform cheap non-destructive checks in parallel where safe:

- local configuration validity
- Tailscale DNS/name resolution
- Gateway version/health
- saved device identity availability
- saved connection profile validity

Do not automatically open SSH unless the active workspace requires it.

## Terminal connection self-test

When the terminal workspace opens:

- resolve host
- connect SSH
- verify pinned host key
- authenticate
- allocate PTY
- detect/create/attach tmux
- verify terminal resize

Record exact failing phase.

## Recovery classes

### Automatic transient recovery

Allowed examples:
- socket timeout
- Wi-Fi to mobile network transition
- temporary Tailscale route loss
- app background/foreground transition
- SSH channel loss with unchanged trusted identity

Use bounded exponential backoff with jitter.

### User-confirmed recovery

Required examples:
- host key changed
- credential revoked
- new device trust needed
- destructive conflict resolution

### Blocking failures

Never auto-bypass:
- host-key mismatch
- invalid trust
- capability denial
- credential integrity failure
- live-trading safety invariant violation

## Session recovery

Remote execution state is owned by tmux, not the Android process.

On reconnect:

1. reconnect transport
2. verify identity again
3. attach existing tmux session
4. request terminal dimensions
5. redraw terminal

Never replay previously typed commands automatically.

## Local diagnostic bundle

Provide a user-triggered diagnostic export containing only non-secret metadata:

- app version
- Android version
- architecture state
- connection phase results
- timestamps
- sanitized host/profile identifiers
- recent structured errors
- build id

Exclude:
- private keys
- passwords
- raw credential tokens
- terminal command history by default
- file contents

## Structured logging

Use structured events rather than arbitrary print lines.

Fields may include:
- event id
- component
- phase
- result
- latency
- recoverability
- correlation id

This supports debugging without scraping text.

## Performance telemetry

Measure locally:
- cold app startup
- terminal screen render
- SSH connect latency
- tmux attach latency
- reconnect duration
- SFTP directory load
- editor open/save

Telemetry must be local/private by default unless an explicit future opt-in design is approved.

## Watchdogs

Use bounded watchdogs for:
- stuck SSH handshake
- PTY allocation timeout
- tmux attach timeout
- SFTP operation timeout

A watchdog may cancel/retry the operation but must not kill unrelated remote processes.

## Auto-repair scope

Allowed automatic repairs:
- recreate an SSH channel
- reopen SFTP channel
- restore foreground service binding
- reattach tmux
- refresh Gateway session when allowed

Forbidden automatic repairs:
- accept a changed host key
- generate trust without approval
- replace credentials silently
- edit backend security policy
- enable live trading

## Health UI

Main status should be concise:
- Готово
- Подключение...
- Требуется действие
- Частично доступно
- Нет связи

Detailed diagnostics remain one tap away.

## Acceptance

Self-test architecture passes when fault injection can distinguish at least:
- no network
- no Tailscale route
- Gateway down
- NucBox down
- SSH authentication failure
- host-key change
- tmux unavailable
- SFTP unavailable

and each state produces the correct Russian recovery action.

## Safety invariants

LIVE_TRADING_ENABLED = NO
live_trading_authority = ABSENT
RESEARCH_ONLY = YES
