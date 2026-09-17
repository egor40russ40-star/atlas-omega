# 40 — Performance Budgets and Regression Gates

## Status
FROZEN ARCHITECTURE ADDENDUM

## Goal
Prevent progressive slowdown as features are added. Performance is a release property, not a late optimization task.

## Metrics
### Startup
Measure:
- process start → first frame;
- first frame → workspace restored;
- workspace restored → terminal reconnect initiated;
- reconnect initiated → shell usable.

### Terminal
Measure:
- input event → transport write enqueue;
- remote output → screen update latency;
- sustained output throughput;
- dropped/coalesced render updates;
- memory growth during long scrollback;
- PTY resize latency.

### Editor/files
Measure:
- open file latency by size class;
- save/atomic write latency;
- directory listing latency;
- diff rendering latency.

### Resource use
Measure:
- idle memory;
- active terminal memory;
- high-output memory plateau;
- CPU during idle and sustained output;
- battery/thermal sanity over sustained session;
- local storage growth.

## Initial engineering budgets
Budgets are targets to validate and tune on real hardware, not fabricated guarantees.

- UI first frame should feel immediate and must not wait for network.
- terminal input pipeline must not intentionally buffer human keystrokes for network batching.
- terminal rendering may batch output frames, but input remains low-latency.
- scrollback and diagnostics are strictly bounded.
- idle polling should approach zero when push/event state is available.
- network reconnect uses bounded backoff rather than tight retry loops.

## Benchmark classes
P0 — local unit/micro benchmarks.
P1 — emulator macrobenchmark where meaningful.
P2 — integration benchmark against test SSH endpoint.
P3 — real-device benchmark on the primary device class.

## Regression detection
Each benchmark stores baseline by release candidate. CI reports delta, not only absolute value.

A regression triggers escalation when it:
- exceeds configured threshold;
- causes unbounded growth;
- increases terminal input latency materially;
- degrades startup enough to affect workflow;
- increases idle wakeups/network polling unexpectedly.

## Performance change routing
UI-only changes run targeted startup/render checks.
Terminal/SSH/session changes run terminal latency/throughput checks.
Storage/files changes run open/save/listing checks.
Architecture/dependency changes run full performance suite.

## Non-goals
Do not sacrifice:
- host identity verification;
- encryption;
- atomic saves;
- correctness of terminal state;
- rollback/evidence;
for benchmark numbers.

## Acceptance
PERFORMANCE_BUDGETS = REQUIRED
REGRESSION_DELTA_REPORT = REQUIRED
UNBOUNDED_SCROLLBACK = FORBIDDEN
NETWORK_BLOCKS_FIRST_FRAME = FORBIDDEN
SECURITY_FOR_SPEED_TRADEOFF = FORBIDDEN
