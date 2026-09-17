# 11. DEVELOPMENT AUTOMATION AND PARALLELIZATION

Status: ARCHITECTURE ONLY
APK build: FORBIDDEN until explicit user command

## Goal

Reduce calendar time of ATLAS Mobile 2 implementation without trading quality for speed. The project must be designed so independent parts can be implemented, tested and integrated in parallel.

## Core rule

Do not build the application as one sequential MainActivity-sized task. Split it into independent workstreams with stable interfaces.

## Parallel workstreams

1. Foundation
   - Gradle/version catalog
   - core models
   - logging
   - navigation contracts
   - localization infrastructure

2. Terminal UI
   - terminal emulator host
   - keyboard accessory
   - tabs
   - font/scroll/search/copy/paste
   - terminal screen state

3. SSH transport
   - connection profiles
   - SSH authentication
   - host-key verification
   - reconnect policy
   - PTY resize

4. Session persistence
   - foreground service
   - session registry
   - tmux attach/create policy
   - reconnect state machine
   - app lifecycle recovery

5. Files and editor
   - SFTP
   - file tree
   - atomic writes
   - editor
   - path:line navigation

6. Control plane
   - Gateway health
   - Machines
   - Jobs
   - capabilities
   - trust state

7. Russian UX
   - strings catalog
   - terminology
   - error mapping
   - accessibility text

8. Test infrastructure
   - fake SSH server
   - fake Gateway
   - deterministic connection-state tests
   - emulator smoke tests
   - real-device checklist

## Interface-first development

Each workstream must begin with interfaces and fixtures before implementation.

Examples:

- TerminalSession
- TerminalTransport
- ConnectionProfileRepository
- FileRepository
- GatewayClient
- DeviceIdentityStore
- SessionPersistence
- RussianErrorMapper

UI depends on interfaces, not concrete SSH/Gateway classes. This allows UI and transport development to proceed in parallel.

## Mock-first rule

Every screen must be runnable against a fake data source before the real backend is connected.

This means:

- Terminal screen can render with a fake PTY stream.
- Machines screen can render fake online/offline machines.
- Jobs screen can use fixture jobs.
- File editor can use an in-memory fake filesystem.

Real transport is connected only after UI behavior is stable.

## Integration cadence

Use short integration checkpoints:

- I0 foundation compiles
- I1 terminal shell renders
- I2 keyboard works against fake terminal
- I3 SSH connects in integration test
- I4 tmux persistence passes
- I5 Files/Editor passes
- I6 Gateway control plane passes
- I7 Russian UX passes
- I8 real-device acceptance

Do not wait until the end to integrate all workstreams.

## Feature flags during implementation

Architectural flags are allowed only for incomplete modules:

- terminal_v2
- session_service_v2
- files_v2
- editor_v2
- control_plane_native_v2

Flags must not alter safety invariants and must be removed or frozen before release candidate.

## AI-assisted implementation model

Use AI only behind deterministic gates:

1. generate or modify code
2. compile changed module
3. run changed-module unit tests
4. run static checks
5. only then integrate

No AI-generated code may bypass tests because it "looks correct".

## Small-commit rule

Prefer small, reversible commits by capability:

- terminal keyboard base
- SSH host-key policy
- tmux attach
- SFTP atomic save

Avoid giant commits spanning unrelated modules.

## Definition of done for a workstream

A workstream is complete only when:

- interface is stable
- unit tests pass
- integration fixture exists
- Russian strings exist
- failure states exist
- no live-trading authority is introduced
- documentation is updated

## Expected acceleration

Target acceleration comes from parallelism and faster feedback, not reduced verification. Expected engineering goal is to make the critical path approximately 2-3x shorter than a fully sequential implementation, subject to actual dependency and CI performance.

## Safety invariants

LIVE_TRADING_ENABLED = NO
live_trading_authority = ABSENT
RESEARCH_ONLY = YES
