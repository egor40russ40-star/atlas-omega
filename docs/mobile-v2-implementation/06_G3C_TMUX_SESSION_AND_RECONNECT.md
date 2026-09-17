# G3C — tmux Session and Reconnect Orchestration

## Implemented
- Strict tmux session-name validation before shell writes.
- Idempotent `tmux new-session -A` bootstrap for attach-or-create behavior.
- TerminalSessionCoordinator separates transport lifecycle from session lifecycle.
- Reconnect policy distinguishes network/app-resume/stream-end from auth/host-key/ambiguous-write failures.
- Pending user input is never replayed after reconnect.
- Ambiguous writes require user acknowledgement.
- Host-key changes and auth failures cannot auto-reconnect.

## Functional effect
A remote coding process can remain alive in tmux while Android disconnects, changes networks, is backgrounded, or reconnects. Reconnection restores transport/session context without replaying the command that was in flight.

## Safety
LIVE_TRADING_ENABLED = NO
LIVE_TRADING_AUTHORITY = ABSENT
AUTO_TRUST_NEW_DEVICE = NO
RESEARCH_ONLY = YES
APK_BUILD = BLOCKED UNTIL G7
