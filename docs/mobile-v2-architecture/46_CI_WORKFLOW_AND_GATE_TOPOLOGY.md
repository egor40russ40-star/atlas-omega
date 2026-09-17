# 46 — CI Workflow and Gate Topology

## Status
PRE-IMPLEMENTATION EXECUTION SPEC

## Goal
Turn architecture gates into a fast, deterministic CI topology.

## Fast Gate
Triggered on feature/module changes.
Runs:
- affected module compile;
- affected unit tests;
- static analysis for touched modules;
- localization checks when UI/resource files change;
- contract compatibility checks.

Target: fast developer feedback; no APK required.

## Integration Gate
Triggered when multiple dependent modules or shared contracts change.
Runs:
- dependent module tests;
- fake/real transport contract suite;
- session/input invariants;
- selected integration tests;
- targeted benchmark checks.

## Full Gate
Triggered by:
- terminal/SSH/session critical changes;
- security/trust changes;
- manifest/permissions;
- dependency/toolchain upgrades;
- release candidate request;
- backend API contract changes.

Runs:
- clean build;
- full unit suite;
- lint/static checks;
- integration suite;
- dependency verification;
- localization completeness;
- APK assemble for candidate stage only;
- artifact integrity/checksum;
- performance regression suite where applicable.

## Parallel jobs
Independent jobs:
- compile/test modules;
- lint/static;
- localization;
- dependency verification;
- benchmarks;
- packaging.

Merge only after required jobs pass.

## Change-aware router
CI reads changed paths and module dependency graph. It must never skip a required downstream module. If classification is uncertain, escalate upward rather than guess downward.

## Cache strategy
Cache:
- Gradle dependencies;
- wrapper/tool downloads;
- build cache where safe.

Cache keys include toolchain/catalog/lock inputs. Release candidate clean-build verification bypasses stale assumptions.

## Failure policy
- fail fast on compile/security/contract break;
- aggregate independent test failures where useful;
- no infinite auto-retry;
- infrastructure retry is bounded and distinct from code failure;
- repair-loop may propose deterministic fixes but does not silently merge them.

## Evidence
Each CI gate emits machine-readable summary:
- commit SHA;
- classification;
- affected modules;
- tests run/skipped with reasons;
- cache status;
- durations;
- artifact SHA when produced;
- gate result.

## Acceptance
FAST_GATE = REQUIRED
INTEGRATION_GATE = REQUIRED
FULL_GATE = REQUIRED
CHANGE_AWARE_ROUTING = REQUIRED
UNCERTAIN_CLASSIFICATION_ESCALATES = YES
APK_EVERY_COMMIT = NO
