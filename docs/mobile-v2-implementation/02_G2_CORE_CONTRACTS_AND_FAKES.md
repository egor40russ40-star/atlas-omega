# G2 — Core Contracts and Fakes

## Status
IMPLEMENTED

Core models now define:
- safety invariants;
- trust state and connection profiles;
- layered connection health and degraded operating modes;
- workspaces and remote-file snapshots;
- terminal lifecycle and modifier state;
- Git working-tree state.

Typed result/error primitives now define stable error domains for network/trust/auth/SSH/PTY/tmux/SFTP/file conflicts/gateway/storage/validation/internal failures.

Deterministic fake data/failure fixtures are available for UI and feature development before real transports are connected.

## Parallel lanes unlocked
- terminal UI/input;
- sessions/tmux orchestration;
- connection UX;
- files/editor/Git UX;
- ATLAS control UX;
- Russian design system and previews;
- transport adapters.

## Safety
LIVE_TRADING_ENABLED = NO
LIVE_TRADING_AUTHORITY = ABSENT
RESEARCH_ONLY = YES

## Gate
G2 source implementation = COMPLETE
G2 compile/test gate = PENDING CI
G3 parallel feature implementation = UNLOCKED
