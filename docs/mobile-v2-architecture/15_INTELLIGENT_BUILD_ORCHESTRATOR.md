# 15. INTELLIGENT BUILD AND IMPLEMENTATION ORCHESTRATOR

Status: ARCHITECTURE ONLY
APK build: FORBIDDEN until explicit user command

## Goal

Use the minimum sufficient verification for each change, then automatically escalate when scope or risk grows.

## Change classes

### Class 0 — Documentation
Validation:
- documentation checks only
- no Android build

### Class 1 — Cosmetic and localization
Validation:
- resources
- targeted UI compile
- localization completeness

### Class 2 — Ordinary feature code
Validation:
- affected-module compile
- affected unit tests
- selected lint

### Class 3 — Terminal, transport and session behavior
Validation:
- module compile
- unit tests
- integration tests
- reconnect/failure tests

### Class 4 — Trust, identity and permission behavior
Validation:
- complete relevant verification set
- full static safety gates
- mandatory Full Gate before acceptance

### Class 5 — Release integration
Validation:
- complete Full Gate
- emulator suite
- package integrity checks
- real-device acceptance when required

## Automatic escalation

Escalate validation when:
- multiple modules are affected
- a public interface changes
- an API contract changes
- dependencies change
- a safety invariant changes
- targeted verification fails unexpectedly

High-risk changes are never downgraded simply to save time.

## Failure classification

Classify CI failures before changing code:
- SOURCE_FAILURE
- TEST_FAILURE
- CONTRACT_FAILURE
- INFRASTRUCTURE_FAILURE
- DEPENDENCY_FAILURE
- FLAKY_SUSPECTED

Infrastructure failures may be retried automatically.
Repeated retry-until-green for flaky or source failures is forbidden.

## Bounded automated repair loop

Permitted development loop:
1. make one scoped change
2. run minimal gate
3. parse deterministic failure
4. make one scoped repair when appropriate
5. rerun the same gate
6. escalate verification when required
7. commit only after required gates pass

The repair loop has a fixed retry budget. Infinite automated patching is forbidden.

## Parallel work queue

Implementation phases are decomposed into atomic tasks with declared dependencies.
Tasks whose dependencies are satisfied may proceed in parallel.

Priority goes to work that unlocks several other workstreams:
- interfaces/models
- fake implementations
- terminal adapter
- session contracts
- test infrastructure

## Reuse-first policy

Before implementing a capability, check whether the project or an approved dependency already provides a suitable primitive.

Do not reimplement standard terminal emulation, SSH protocol, or Android lifecycle primitives without a concrete reason.

## Architecture drift checks

Automated structural checks should catch drift such as:
- UI layers owning transport responsibilities
- unrelated features depending directly on each other
- activity classes accumulating session/business logic
- duplicated connection state machines

## Commit evidence

Implementation commits should record:
- change class
- gates executed
- result
- duration
- safety invariant status

## Metrics

Track:
- task lead time
- first-pass success rate
- repair iterations per task
- Fast Gate duration
- Full Gate duration
- real-device-only defects

Optimization decisions should use measured bottlenecks.

## Safety invariants

LIVE_TRADING_ENABLED = NO
live_trading_authority = ABSENT
RESEARCH_ONLY = YES
