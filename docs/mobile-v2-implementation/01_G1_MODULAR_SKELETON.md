# G1 — Modular Skeleton

## Status
STRUCTURE CREATED

The mobile project is now split into bounded modules matching the frozen architecture:
- core: model/result/security/network/ui;
- features: terminal/sessions/connections/files/editor/git/atlas/ai/settings;
- transports: ssh/sftp/gateway;
- storage: local;
- testing: fakes.

## Build-speed defaults
- Gradle build cache enabled.
- Parallel Gradle execution enabled.
- Configuration cache enabled with warnings surfaced.
- AndroidX/non-transitive R retained.

## Compatibility
The existing `:app` alpha1 source is retained unchanged as reference/rollback while new modules are introduced around it.

## Safety
LIVE_TRADING_ENABLED = NO
LIVE_TRADING_AUTHORITY = ABSENT
RESEARCH_ONLY = YES

## Gate
G1 source structure = COMPLETE
G1 compile gate = PENDING CI
G2 contracts/fakes = UNLOCKED
