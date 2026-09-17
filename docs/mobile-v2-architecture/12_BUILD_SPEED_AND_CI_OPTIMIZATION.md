# 12. BUILD SPEED AND CI OPTIMIZATION

Status: ARCHITECTURE ONLY
APK build: FORBIDDEN until explicit user command

## Goal

Minimize feedback time from code change to verified result. Full APK assembly must not be the default validation step for every edit.

## Two-tier verification pipeline

### Fast Gate

Runs for ordinary implementation commits and should be optimized for seconds/minutes, not full release validation.

Tasks:
- compile changed Kotlin modules
- unit tests for changed modules
- static safety assertions
- localization key checks
- dependency lock verification
- selected lint rules
- architecture dependency checks

### Full Gate

Runs for integration milestones and release candidates.

Tasks:
- all unit tests
- full Android lint
- assembleDebug / release candidate artifact as appropriate
- emulator smoke suite
- SSH integration suite
- Gateway contract suite
- APK integrity/hash checks
- Russian resource completeness
- real-device gate when required

## Change-aware CI

CI should calculate affected modules from changed paths.

Examples:
- terminal-ui change does not rebuild unrelated Gateway fixtures
- docs-only change triggers no Android compilation
- localization-only change runs resource and screenshot checks
- transport change runs SSH integration tests

Full gate is still mandatory at milestone boundaries.

## Gradle optimization targets

When implementation starts, enable and verify where compatible:

- Gradle build cache
- configuration cache
- parallel execution
- daemon reuse in persistent environments
- dependency locking
- version catalog
- incremental Kotlin compilation
- stable compiler arguments

Do not enable an optimization if it causes nondeterministic builds.

## Repository modularization for build speed

Target module shape:

- :app
- :core:model
- :core:ui
- :core:network
- :core:security
- :terminal:emulator
- :terminal:transport
- :terminal:session
- :feature:terminal
- :feature:connections
- :feature:files
- :feature:editor
- :feature:machines
- :feature:jobs
- :feature:settings
- :testing:fakes

A change in one feature should not force recompilation of every feature.

## Dependency direction

Feature modules may depend on core interfaces.

They must not depend directly on unrelated feature modules.

Example:

feature:editor -> core:model + FileRepository interface
feature:terminal -> terminal:session + terminal:emulator
feature:machines -> GatewayClient interface

This improves both build speed and replaceability.

## CI parallel jobs

Full Gate should split independent work:

Job A: compile + unit
Job B: lint/static analysis
Job C: SSH integration
Job D: Gateway contract tests
Job E: emulator UI smoke tests

Artifact packaging begins only after required jobs pass.

## Dependency download optimization

Use CI caches keyed by:

- Gradle version
- lockfile/version catalog hash
- build logic hash

Do not cache produced APK as a substitute for a reproducible build.

## Prebuilt test fixtures

Use small deterministic fixtures for:

- SSH host
- SFTP filesystem
- terminal output
- Gateway JSON

Avoid booting unnecessary infrastructure for pure JVM tests.

## No-build architecture work

Changes under docs/mobile-v2-architecture/ must never trigger APK assembly.

This is required to keep architecture iteration fast.

## Build time telemetry

Every full build should record:

- total duration
- Gradle configuration duration
- Kotlin compile duration
- lint duration
- unit test duration
- integration duration
- APK assembly duration
- cache hit/miss information when available

Track regressions rather than guessing.

## Performance budgets

Initial targets, to be measured and revised from real CI data:

- Fast Gate: <= 3 minutes
- changed-module unit feedback: <= 90 seconds when cached
- Full Gate: <= 10 minutes excluding real-device manual interaction

These are targets, not guarantees.

## Fail-fast order

Run cheapest blockers first:

1. architecture/safety assertions
2. compilation
3. unit tests
4. lint
5. integration
6. emulator
7. package artifact

Never spend minutes packaging an APK after a basic safety or compile failure.

## Safety invariants

LIVE_TRADING_ENABLED = NO
live_trading_authority = ABSENT
RESEARCH_ONLY = YES
