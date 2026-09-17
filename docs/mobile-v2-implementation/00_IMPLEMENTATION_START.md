# G0 — Implementation Start

## Authorization
User explicitly authorized transition from architecture-only to implementation-active on 2026-09-17.

## Immutable references
- Architecture freeze commit: `075853cd39b43a14271ae40bbaab3f8b7d886f68`
- Architecture branch: `atlas-mobile-v2-architecture`
- Recovery branch: `atlas-mobile-v2-recovery-preimplementation`
- Implementation branch: `atlas-mobile-v2-implementation`

## Rules carried into implementation
- Terminal-first remains the primary product principle.
- Russian-first remains the primary UX principle.
- Existing alpha1 code remains available as reference/rollback until replacement gates pass.
- Backend RC2 compatibility is preserved unless an additive contract is explicitly implemented and tested.
- No new device is trusted automatically.
- No secret/private key is committed to the repository.
- No shell command is silently re-sent after an ambiguous reconnect.
- No APK is promoted before its candidate gate.
- Real-device certification is required before any completion claim.

## Safety invariants
- `LIVE_TRADING_ENABLED = NO`
- `LIVE_TRADING_AUTHORITY = ABSENT`
- `RESEARCH_ONLY = YES`

## Current gate
- G0 Recovery/branch isolation: COMPLETE
- G1 Modular skeleton: STARTING
- G2 Core contracts + fakes: LOCKED until G1 structure exists
- G7 First APK candidate: BLOCKED
