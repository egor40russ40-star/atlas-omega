# 44 — Test Vectors and Failure-Injection Plan

## Status
PRE-IMPLEMENTATION EXECUTION SPEC

## Goal
Prepare deterministic test vectors before implementation so each lane can validate behavior without waiting for full integration.

## Terminal vectors
- normal ASCII typing;
- Cyrillic input/output;
- ANSI colors;
- cursor movement;
- full-screen TUI;
- resize portrait↔landscape;
- high-output stream;
- long scrollback;
- paste single-line;
- paste multi-line;
- CTRL/ALT/SHIFT combinations;
- physical keyboard parity.

## Session vectors
- clean connect;
- auth fail;
- host identity mismatch;
- network drop before shell ready;
- network drop while idle;
- network drop during output;
- Android background/restore;
- process recreation;
- tmux attach existing;
- tmux create missing;
- repeated reconnect must be idempotent.

## Input-delivery invariant tests
- never resend uncertain shell input;
- queued local keystrokes have explicit delivery state;
- reconnect restores session, not previous command stream.

## File/SFTP vectors
- list directory;
- open small/medium/large text file;
- save unchanged;
- save changed;
- remote file changed after open -> conflict;
- connection loss during write -> no partial final file;
- Unicode/Cyrillic path;
- permission denied;
- missing file;
- rename/atomic replace behavior.

## Git vectors
- clean tree;
- modified file;
- untracked file;
- staged changes;
- conflicting changes;
- long diff;
- binary file presence;
- branch/status read;
- commit preparation with explicit review.

## Gateway vectors
- ready;
- unauthorized;
- trusted device required;
- Gateway unavailable but SSH works;
- SSH unavailable but Gateway works;
- additive capability absent;
- incompatible API version.

## Localization vectors
- every native screen in Russian;
- long Russian labels on compact phone;
- no hard-coded English user-facing strings outside allowed technical output;
- plural/error/status variants;
- accessibility labels in Russian.

## Performance/failure injection
Inject:
- latency;
- temporary packet loss;
- reconnect storms;
- large terminal output;
- slow SFTP;
- file conflict race;
- low-memory recreation;
- unavailable telemetry endpoint.

## Security vectors
- changed host key -> block;
- unknown device -> pending/not trusted;
- invalid recovery archive -> reject;
- diagnostic redaction -> secret patterns absent;
- remote capability cannot elevate device authorization.

## Acceptance
DETERMINISTIC_TEST_VECTORS = READY
FAILURE_INJECTION = REQUIRED
RECONNECT_DUPLICATE_INPUT_TEST = REQUIRED
RUSSIAN_UI_VECTOR_SET = REQUIRED
