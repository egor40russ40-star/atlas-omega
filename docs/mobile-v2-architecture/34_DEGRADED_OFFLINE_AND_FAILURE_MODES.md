# 34 — Degraded, Offline and Failure Modes

## Status
FROZEN ARCHITECTURE ADDENDUM

## Goal
ATLAS Mobile 2 must remain understandable and useful when only part of the infrastructure is available.

## Rule
Never collapse all connectivity into one ONLINE/OFFLINE flag.

## Layer states
- DEVICE_NETWORK
- TAILSCALE_REACHABILITY
- GATEWAY_REACHABILITY
- GATEWAY_AUTH
- NUCBOX_REACHABILITY
- SSH_AUTH
- PTY_SESSION
- TMUX_SESSION
- SFTP
- CONTROL_API

Each layer has explicit states: UNKNOWN, CHECKING, READY, DEGRADED, FAILED.

## Operating modes
### FULL
Gateway + NucBox + terminal/data services available.

### TERMINAL_ONLY
NucBox SSH works, Gateway/control plane unavailable. Terminal, tmux, SFTP and local workspace context may continue.

### CONTROL_ONLY
Gateway works but NucBox SSH unavailable. Machines, jobs, health and diagnostics remain available; terminal is read-only unavailable, not falsely marked connected.

### LOCAL_CONTEXT_ONLY
No remote connectivity. App can show cached workspace metadata, recent file paths, snippets, local settings and diagnostics. No remote mutation is queued silently.

### RECOVERY
Connection is being re-established. User input must not be replayed unless delivery semantics prove it was not sent.

## Mutation policy while offline
- no hidden command queue for shell input;
- no delayed automatic Git write;
- no delayed automatic file overwrite;
- safe local drafts may be stored as drafts only;
- after reconnect, remote state is refreshed before mutation.

## Terminal reconnect
Terminal recovery sequence:
1. regain network;
2. regain Tailscale reachability;
3. SSH reconnect;
4. verify host identity;
5. attach existing tmux session idempotently;
6. resize PTY;
7. resume output stream;
8. restore UI scroll/focus context without replaying commands.

## UX
Top-level status examples:
- `Терминал готов`;
- `Шлюз недоступен, терминал работает`;
- `NucBox недоступен`;
- `Восстановление соединения…`;
- `Работа без сети: только локальный контекст`.

Technical details are expandable and never replace the user-facing Russian explanation.

## Failure boundaries
A failure in:
- Gateway must not kill an already usable direct terminal;
- one terminal tab must not terminate other tabs;
- SFTP must not terminate SSH terminal sessions;
- AI feature must not block code/terminal/files;
- telemetry must never block application startup.

## Acceptance
DEGRADED_MODES = EXPLICIT
SILENT_OFFLINE_MUTATION = FORBIDDEN
SHELL_INPUT_REPLAY = FORBIDDEN
TERMINAL_ONLY_MODE = REQUIRED
CONTROL_ONLY_MODE = REQUIRED
