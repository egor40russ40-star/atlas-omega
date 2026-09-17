# 41 — Architecture Decisions and Risk Register

## Status
FROZEN ARCHITECTURE ADDENDUM

## Goal
Make key choices explicit so implementation does not silently re-open settled architecture or repeat alpha1 mistakes.

## Core ADRs
### ADR-001 — Terminal First
Decision: terminal is the primary workspace, not a secondary screen.
Reason: main use case is writing/running code from phone.

### ADR-002 — Direct SSH/Tailscale Data Plane
Decision: terminal PTY uses direct SSH over Tailscale; Gateway remains control plane.
Reason: lower latency, fewer bottlenecks, terminal survives Gateway degradation.

### ADR-003 — tmux Owns Remote Process Continuity
Decision: Android process does not own long-running shell processes.
Reason: mobile lifecycle is unreliable for process continuity.

### ADR-004 — Russian First
Decision: native app UI is Russian by default; raw Linux/tool output remains original.

### ADR-005 — Explicit Trust
Decision: new device/host identity is never silently trusted.

### ADR-006 — Preview Before Mutation
Decision: AI/code/file/git mutations use preview/approve/apply/test where applicable.

### ADR-007 — Modular/Parallel Build
Decision: features are isolated into modules/interfaces to enable parallel implementation and targeted CI.

### ADR-008 — No APK Until Explicit User Command
Decision: architecture work does not silently trigger implementation/release.

## Risk register
### R1 — Terminal UX still feels worse than Termius
Mitigation: real-device ergonomic benchmarks, configurable keyboard, fullscreen default, landscape-first, physical keyboard tests.

### R2 — SSH library limitations
Mitigation: transport abstraction, integration contract tests, pinned dependency, ability to replace implementation without rewriting UI.

### R3 — Android lifecycle kills connection
Mitigation: foreground service only while needed + tmux remote continuity + idempotent reconnect.

### R4 — Reconnect duplicates commands
Mitigation: single-writer input queue; never replay uncertain shell input.

### R5 — Large output freezes UI
Mitigation: bounded buffers, backpressure, render batching, performance gate.

### R6 — SFTP overwrites remote edits
Mitigation: metadata/version check, conflict UI, atomic write.

### R7 — AI silently damages code
Mitigation: diff preview, explicit approval, atomic apply, targeted tests, rollback.

### R8 — Russian localization drifts
Mitigation: centralized resource catalog, missing-string CI checks, real-device Russian review.

### R9 — Dependency update breaks terminal stack
Mitigation: dependency governance D0–D4 and lock/verification gates.

### R10 — Feature flags bypass authorization
Mitigation: effective capability is intersection of client support, server support and device authorization; remote config cannot grant privilege.

### R11 — Diagnostics leak secrets
Mitigation: redaction gate, bounded local logs, secret fields excluded by design.

### R12 — Architecture becomes too complex and slows development
Mitigation: thin contracts, module ownership, minimal sufficient gates, no abstraction without concrete ownership/use case.

## Change control
Any implementation proposal that contradicts an ADR must:
1. identify the ADR;
2. document why it no longer holds;
3. assess migration/security/performance impact;
4. update architecture first;
5. only then modify implementation.

## Acceptance
ADR_REGISTER = READY
RISK_REGISTER = READY
SILENT_ARCHITECTURE_DRIFT = FORBIDDEN
