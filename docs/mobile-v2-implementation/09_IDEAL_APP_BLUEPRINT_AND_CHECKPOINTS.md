# ATLAS Mobile 2 — Ideal App Blueprint + Checkpoint Plan

Date: 2026-09-19  
Status: IMPLEMENTATION PLAN / ACTIVE  
Safety baseline: RESEARCH_ONLY = YES, LIVE_TRADING_ENABLED = NO

## 1. Mission

ATLAS Mobile 2 is the operator cockpit for ATLAS OMEGA.

The phone must let one person safely:

- understand the current ATLAS state in seconds;
- operate multiple development machines without remembering connection details;
- open a persistent terminal and recover it after disconnects;
- browse/edit files and review Git changes;
- launch repeatable tests/builds/research jobs without typing shell commands;
- inspect failures, logs, evidence and checkpoints;
- continue work from phone, PC or VM without losing context;
- receive meaningful incidents/notifications;
- never accidentally gain live-trading authority.

The product is not “a terminal app with extra tabs”. It is a mobile control plane whose
terminal is one expert tool among several.

## 2. Source-of-truth architecture retained

The technical architecture already established several non-negotiable boundaries:

- Mobile Control Gateway is the BFF/control plane, not an ATLAS canonical writer.
- ATLAS Projection Adapter is read-only.
- Developer automation and interactive shell are separate.
- Machine/provider abstractions hide topology from normal UI.
- Developer jobs are preferred over arbitrary shell for repeatable work.
- No Mobile security zone contains live-trading permission.
- Offline state is read-only and must not replay privileged requests.

Real-device G8 testing adds one implementation conclusion:

- native Android is valuable for Android Keystore, file import, terminal keyboard,
  clipboard, notifications and lifecycle;
- direct SSH is retained as a DEV/recovery transport while the normal long-term control
  plane still converges on Gateway + brokered providers/jobs.

## 3. Product information architecture

### Home — “what needs my attention?”

One screen answers:

- overall ATLAS health;
- current mode;
- machines online/offline/degraded;
- research/test activity;
- failed gates/jobs;
- unresolved incidents;
- last successful checkpoint;
- stale data warnings;
- explicit safety strip: RESEARCH_ONLY / LIVE authority absent.

No raw logs on Home.

### Work

Primary development workspace:

1. Terminal
2. Code
3. Files
4. Git
5. Jobs

Context is shared: machine + workspace + active task + branch.

### Machines

Machine cards for:

- NucBox;
- Cloud VM;
- future Windows/Linux workers.

Each machine owns:

- profile id/title;
- preferred and fallback network endpoints;
- SSH identity reference;
- workspace roots;
- capabilities;
- provider bindings;
- host-key trust state;
- health/freshness;
- resource summary;
- active sessions/jobs.

### ATLAS

Read-only operational domain:

- system status;
- pipeline/gates;
- research;
- strategy candidates;
- paper/forward state;
- risk/safety;
- evidence/reports;
- incidents.

### More

- Connections
- Monitoring
- Security
- Notifications
- Settings
- About/build/checkpoints

## 4. Terminal UX

Terminal must be usable for hours from a phone.

Required:

- deterministic command input field;
- explicit Paste, Enter and Send;
- paste never executes;
- multiline send requires confirmation;
- visible ESC/TAB/CTRL/arrows/Home/End;
- code-symbol row;
- resize on orientation/window changes;
- tmux persistence;
- reconnect without replaying uncertain commands;
- searchable scrollback later;
- copy/select;
- font size controls;
- landscape layout;
- external keyboard support;
- command snippets/history as optional convenience, never hidden execution.

G8 found the first alpha2 keyboard insufficient. CP9 fixed explicit Paste/Enter/Send.

## 5. Code + Files

Files:

- machine/workspace-aware root;
- breadcrumb navigation;
- favorites/recent files;
- safe SFTP reads;
- size/type guard;
- hidden files toggle;
- upload/download later;
- never silently leave approved workspace.

Editor:

- syntax-aware editor in later checkpoint;
- dirty indicator;
- atomic save;
- remote-change conflict detection;
- line numbers/search;
- undo/redo;
- open in terminal;
- run selection / insert selection with explicit semantics.

## 6. Git

Default flow is diff-first:

status → select file → diff → stage/unstage → commit.

Rules:

- no force push;
- no destructive reset as a normal action;
- branch/repository always visible;
- commit requires explicit message;
- push/pull are separate later capabilities with confirmation and conflict UX;
- checkpoint branches are first-class ATLAS workflow artifacts.

## 7. Jobs / automation

Repeated work should become registered jobs, not shell snippets.

Examples:

- changed tests;
- package tests;
- full tests;
- static scan;
- APK build;
- release candidate build;
- handoff generation;
- backup request;
- research batch;
- benchmark;
- soak test.

Each job shows:

- target machine;
- action spec/version;
- state;
- prerequisites;
- start/end/duration;
- progress when available;
- log tail;
- artifacts;
- failure reason;
- retry policy;
- checkpoint generated.

Phone can disconnect after durable job creation.

## 8. Network model

Normal user experience must not depend on memorizing MagicDNS/IPs.

A machine will ultimately expose route candidates:

- preferred private/brokered route;
- Tailscale DNS/IP where available;
- approved public protected endpoint;
- recovery endpoint.

Route health is measured independently from SSH authentication.

Rules:

- never auto-trust a new host key;
- fallback endpoint does not inherit host trust blindly;
- distinguish DNS failure, TCP failure, host-key block and auth failure;
- app explains the failing layer in Russian;
- low-level detail is expandable.

G8 demonstrated why this is required: Tailnet TCP/DNS may fail while the VM public SSH
path remains healthy.

## 9. Security

- credentials in Android Keystore only;
- no private keys in profile storage/logs/checkpoints;
- host-key pinning mandatory;
- credential import is explicit;
- credential removal explicit;
- secret-bearing clipboard warnings later;
- biometric step-up for high-risk admin zones later;
- no broker/live credentials in Mobile;
- no LIVE authority;
- audit all state-changing control-plane actions.

## 10. Monitoring and incidents

Layer model:

NETWORK → ROUTE/DNS → GATEWAY → SSH → SFTP/GIT → PTY → TMUX → NODE → ATLAS.

Never collapse all of these into one ONLINE label.

Monitoring shows:

- current state;
- last checked;
- technical detail;
- suggested next action;
- retry.

Incidents deduplicate repeated failures.

## 11. Offline/lifecycle

- render last safe snapshot immediately with age;
- offline is explicitly read-only;
- preserve unsent editor draft locally;
- preserve current machine/workspace/navigation;
- terminal relies on tmux for remote continuity;
- process death must not imply command replay;
- app upgrade must preserve profiles/trust/credentials whenever package/signing identity allows.

## 12. UI details

- Russian-first;
- Linux/Git/program output unmodified;
- dark theme baseline;
- large touch targets;
- no critical action hidden behind horizontal scrolling;
- compact phone portrait layout;
- landscape terminal optimized;
- error text: human summary first, technical detail second;
- every long operation shows state rather than an indefinite spinner;
- Back returns to logical prior context;
- selected machine is visible whenever an action is machine-specific.

## 13. Checkpoint implementation sequence

Each checkpoint obeys:

one bounded change → atomic commit → CI gate → immutable checkpoint branch → next.

### CP9 — terminal input + workspace correctness — GREEN

- explicit Paste/Enter/Send;
- multiline confirmation;
- machine-specific workspace root;
- CI compile/tests/lint/safety/legacy all green.

### CP10 — machine/profile registry foundation

- migrate one-profile storage to multi-profile registry;
- preserve active profile;
- keep rollback-compatible legacy mirror;
- no credential migration into normal preferences;
- initialize Files/Git context from active profile.

Gate: compile/tests/lint/safety/legacy.

### CP11 — Connections UX

- profile list;
- add/edit/select;
- NucBox + Cloud VM presets only as user-editable suggestions;
- per-profile workspace;
- credential state;
- trust state;
- no accidental credential sharing across profiles.

### CP12 — route diagnostics and fallback model

- structured route candidates;
- DNS/TCP/SSH layer diagnostics;
- safe endpoint fallback;
- Russian errors + expandable technical detail.

### CP13 — terminal professional UX

- verified IME;
- copy/select;
- landscape;
- resize;
- external keyboard;
- complete programmer keyboard;
- real-device bash/tmux/nano/vim gate.

### CP14 — Files professional UX

- breadcrumb;
- favorites;
- hidden files;
- refresh/conflict UX;
- approved-root boundary.

### CP15 — Editor v2

- line numbers/search/undo;
- selection actions;
- conflict resolution;
- explicit insert/run semantics.

### CP16 — Git v2

- repository header;
- diff quality;
- stage/unstage/commit;
- safe pull/push design;
- checkpoint actions.

### CP17 — Monitoring v2

- layered diagnostics;
- timestamps;
- suggested action;
- incident grouping.

### CP18 — Gateway + Machine Center

- machine cards;
- capabilities;
- resources;
- provider health;
- read-only status aggregation.

### CP19 — Developer Jobs

- durable queue UI;
- logs/artifacts;
- retry;
- real process cancellation only when backend implements it;
- APK/test/handoff jobs.

### CP20 — ATLAS read-only cockpit

- status;
- gates;
- research;
- candidates;
- evidence;
- risk/safety.

### CP21 — notifications/offline/deep links

- safe cached snapshots;
- incident notifications;
- deep link back to context.

### CP22 — security hardening

- biometric step-up where needed;
- audit views;
- secret/clipboard hardening;
- backup/restore rules;
- threat-model tests.

### CP23 — performance/soak/recovery

- long terminal sessions;
- network switching;
- process death;
- app restart;
- VM/NucBox failover;
- large repos/files;
- battery/memory.

### CP24 — release candidate

- deterministic APK;
- signature/upgrade test;
- clean install + upgrade migration;
- full regression;
- handoff bundle;
- rollback artifact.

## 14. Definition of “ideal enough to rely on”

The app is not considered complete because screens exist. It is complete only when:

- a real phone can switch between NucBox and VM without re-entering topology;
- terminal input is fully usable;
- normal development work rarely requires Termux;
- routine tests/builds run as durable jobs;
- Git changes are reviewable before mutation;
- machine/network failures are correctly localized;
- credentials survive restart but never leak;
- checkpoints make every development step recoverable;
- ATLAS state is visible without giving Mobile live-trading authority;
- long-duration real-device soak passes.
