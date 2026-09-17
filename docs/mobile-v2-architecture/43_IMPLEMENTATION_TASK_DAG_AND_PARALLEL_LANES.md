# 43 — Implementation Task DAG and Parallel Lanes

## Status
PRE-IMPLEMENTATION EXECUTION SPEC

## Goal
Minimize critical path by starting independent workstreams as soon as shared contracts are stable.

## Gates
G0 Recovery + branch isolation
G1 Modular Gradle skeleton
G2 Core contracts + fakes
G3 Parallel feature lanes
G4 Module gates
G5 Integration
G6 Emulator/device preflight
G7 Candidate APK
G8 Real-device terminal certification
G9 Full feature certification
G10 Release candidate

## Dependency DAG
G0 -> G1 -> G2

After G2, run in parallel:
- LANE A: terminal renderer + programmer keyboard
- LANE B: SSH transport + host identity
- LANE C: session service + tmux lifecycle
- LANE D: files/SFTP + editor + Git read workflow
- LANE E: Gateway/control-plane client + machines/jobs/health
- LANE F: Russian resources + navigation + accessibility
- LANE G: diagnostics + test fakes + benchmark harness

Dependencies:
A+B+C -> terminal integration
B+D -> remote file integration
E+F -> native control UI
A+C+F -> terminal-first shell UX
G is continuous and attaches gates to every lane

## Merge order
1. core contracts
2. testing fakes
3. lane-local implementations
4. transport/session integration
5. UI integration
6. real-device hardening

## Parallelism rule
A lane may start only when its consumed interface is frozen. Implementation detail from another lane must not be imported directly across module boundary.

## Blocker handling
If a lane blocks:
- continue independent lanes;
- expose blocker through typed contract/test;
- do not bypass architecture by adding cross-module shortcut;
- escalate gate only for affected surface.

## Milestone artifacts
Every gate produces:
- commit SHA;
- changed modules;
- test summary;
- performance delta where relevant;
- known blockers;
- next unlocked lanes.

## Acceptance
TASK_DAG = READY
PARALLEL_LANES = 7
CROSS_LANE_SHORTCUTS = FORBIDDEN
GATE_EVIDENCE = REQUIRED
