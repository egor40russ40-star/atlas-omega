# 47 — Critical Path, Speed Model and Execution Metrics

## Status
PRE-IMPLEMENTATION EXECUTION SPEC

## Goal
Optimize for elapsed time to a reliable real-device candidate, not raw lines of code or number of commits.

## Critical path
Expected critical path:
G0 recovery/branch
-> G1 modular skeleton
-> G2 core contracts/fakes
-> A+B+C terminal integration
-> G5 integration
-> G6 device preflight
-> G7 candidate APK
-> G8 real-device terminal certification
-> G9 full feature certification

Files/editor/Git, Gateway/native control, localization and diagnostics should progress in parallel after G2 and join before G9.

## Speed levers
1. contract-first implementation;
2. fake-first UI development;
3. parallel lanes;
4. generated boilerplate;
5. affected-module Fast Gate;
6. dependency/cache stability;
7. bounded automated repair of deterministic failures;
8. candidate APK only at milestone gates;
9. real-device feedback as early as terminal integration is usable.

## Metrics
Track:
- time G0->G2;
- time to first compiling terminal module;
- time to first fake-terminal UI;
- time to first real SSH shell;
- time to first tmux persistence pass;
- time to first real-device terminal session;
- median Fast Gate duration;
- median Integration Gate duration;
- Full Gate duration;
- cache hit rate;
- failed-build root-cause categories;
- rework caused by contract changes;
- number of cross-lane blockers;
- time from failure to deterministic diagnosis.

## Optimization rule
Optimize the longest dependency chain first. Do not speed a non-critical lane by creating architectural debt on the critical path.

## Rework budget
A high rate of interface churn means implementation started too early. If core contracts repeatedly change after multiple lanes depend on them, pause lane expansion and stabilize contracts.

## Automated repair budget
Only deterministic, local failures may use automated repair loops, such as:
- missing import;
- formatting/static issues;
- known generated-code mismatch;
- straightforward compile incompatibility with clear diagnostics.

Do not auto-repair:
- trust/security semantics;
- terminal input delivery semantics;
- destructive file conflicts;
- authorization;
- ambiguous architecture failures.

## Quality floor
No speed optimization may remove:
- real-device gate;
- security/trust verification;
- terminal/session invariants;
- Russian UI acceptance;
- rollback/recovery evidence.

## Planning model
Use measured gate times from the first implementation week to replace estimates. Future scheduling is based on observed throughput, not assumed coding speed.

## Acceptance
CRITICAL_PATH_MODEL = READY
PARALLELISM_MEASURED = YES
GATE_DURATION_METRICS = REQUIRED
SECURITY_FOR_SPEED_TRADEOFF = FORBIDDEN
REAL_DEVICE_FEEDBACK_EARLY = REQUIRED
