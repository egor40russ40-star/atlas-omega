# 33 — Dependency, Version and Supply-Chain Governance

## Status
FROZEN ARCHITECTURE ADDENDUM

## Goal
Make ATLAS Mobile 2 fast to build and safe to maintain by preventing dependency drift, surprise API breakage, and uncontrolled transitive upgrades.

## Principles
- Pin critical build/runtime versions explicitly.
- Prefer version catalogs and one source of truth.
- Never upgrade terminal/SSH/crypto libraries implicitly through an unrelated BOM change.
- Keep compileSdk/targetSdk/minSdk decisions explicit and reviewed.
- Separate routine dependency updates from architecture changes.
- No secrets, signing keys, tokens, host credentials, or private material in repository configuration.

## Dependency classes
### Class D0 — Build-only
Gradle plugins, lint, test tooling.

### Class D1 — UI
Compose, Material, navigation, lifecycle.

### Class D2 — Terminal/Data Plane Critical
Terminal emulator, SSH, SFTP, PTY integration, encoding.

### Class D3 — Security Critical
Crypto, secure storage wrappers, certificate/host-key handling.

### Class D4 — Control Plane
HTTP/WebSocket/API serialization.

D2/D3 changes always require Full Gate + integration regression. D0/D1 may use targeted gates unless transitive changes touch D2/D3.

## Version governance
Use a single version catalog for all dependencies. Every dependency has:
- owner module;
- class D0–D4;
- current version;
- reason for pinning;
- minimum test gate;
- known compatibility notes.

## Update policy
Automated update discovery is allowed. Automated merging is not.

Flow:
1. detect candidate update;
2. compute dependency diff;
3. classify risk;
4. build isolated candidate;
5. run minimum gate;
6. escalate when terminal/security/API surface changed;
7. publish report;
8. human approval before promotion.

## Reproducibility
- lock dependency graph for candidate/release builds;
- store checksums/verification metadata supported by Gradle;
- build from clean checkout for release candidate;
- record Java/Gradle/AGP/Kotlin/SDK versions in build evidence.

## Supply-chain guard
CI must fail if:
- an unapproved repository is added;
- dependency verification changes unexpectedly;
- dynamic versions (`+`, `latest`) are introduced;
- a critical library changes without the required gate;
- release build uses an unpinned toolchain.

## Speed optimization
Dependency resolution should be cached, but cache keys must include lockfiles/catalog/toolchain versions. Cache speed must never override integrity checks.

## Acceptance
DEPENDENCY_GOVERNANCE = READY
DYNAMIC_VERSIONS = FORBIDDEN
CRITICAL_TRANSITIVE_DRIFT = BLOCKED
REPRODUCIBLE_TOOLCHAIN = REQUIRED
