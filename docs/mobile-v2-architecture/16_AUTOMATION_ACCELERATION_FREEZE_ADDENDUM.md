# 16. AUTOMATION AND ACCELERATION — ARCHITECTURE FREEZE ADDENDUM

Status: FROZEN ARCHITECTURE ADDENDUM
Implementation: NOT STARTED
APK build: FORBIDDEN until explicit user command

## Added architectural requirements

The following are now mandatory parts of ATLAS Mobile 2 implementation.

### 1. Parallel development
Independent terminal, transport, session, files/editor, control-plane, localization and testing workstreams must use stable interfaces and fakes so they can progress concurrently.

### 2. Fast feedback
Every code change must use a Fast Gate first where appropriate. Full APK assembly is reserved for integration/release gates rather than every edit.

### 3. Change-aware CI
CI must understand the affected area and avoid rebuilding unrelated modules. Documentation-only architecture changes must not build Android artifacts.

### 4. Modular Android structure
The implementation must be split into core, terminal and feature modules sufficiently to support incremental compilation and clear dependency direction.

### 5. Repetitive-code automation
API models, feature scaffolding, error catalogs, test fakes and terminal keyboard definitions should be generated or data-driven where this reduces duplication without hiding critical behavior.

### 6. Self-diagnostics
The app must expose layered health rather than one ONLINE flag and must identify whether a failure belongs to network, Gateway, node, SSH, PTY, tmux, SFTP or trust/permission state.

### 7. Safe automatic recovery
Transient connection/session failures should recover automatically with bounded retry policy. Identity/trust changes and blocking conditions must require explicit action.

### 8. Intelligent validation routing
Every implementation change is classified by scope/risk and mapped to the smallest sufficient verification set. Validation automatically escalates for cross-module, contract, dependency or high-risk changes.

### 9. Bounded autonomous repair
Deterministic compile/test failures may enter a limited automated repair loop. Infinite patch/retry loops are forbidden.

### 10. Measurement-driven optimization
Development acceleration must be measured using real metrics rather than assumed.

Required measurements:
- Fast Gate duration
- Full Gate duration
- Kotlin compile time
- test duration
- cache effectiveness
- SSH integration duration
- emulator duration
- task lead time
- repair iterations
- real-device escaped defects

## Target development strategy

When implementation is authorized:

1. freeze interfaces first
2. create fakes and fixtures
3. run independent workstreams in parallel
4. integrate frequently through short gates
5. reserve full APK builds for milestones
6. run emulator/integration automatically
7. run real-device certification only after all machine gates pass

## Target speed goals

These are engineering targets to validate with measurements, not promises:

- critical-path implementation materially shorter than sequential development
- Fast Gate target <= 3 minutes
- cached changed-module feedback target <= 90 seconds
- Full Gate target <= 10 minutes excluding real-device interaction
- architecture/docs edits trigger zero APK builds

## What is explicitly not optimized away

Speed must never remove:
- host identity verification
- trust checks
- command execution safety
- file conflict protection
- integration testing
- Russian UX verification
- real-device acceptance
- rollback capability

## Build trigger rule

Architecture phase ends here.

The following remain blocked until an explicit user command to begin implementation:
- Android source restructuring
- new backend endpoint implementation
- new APK compilation
- deployment
- installation package release

## Safety invariants

LIVE_TRADING_ENABLED = NO
live_trading_authority = ABSENT
RESEARCH_ONLY = YES
