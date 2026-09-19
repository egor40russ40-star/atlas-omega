# CP12B1 — Safe SSH route fallback

Date: 2026-09-19

## Goal

A machine profile can have a primary SSH route plus approved fallback routes.
Network failure on one route must not force the user to reconfigure the machine manually.

## Implemented

- ConnectionProfile now owns ordered SSH endpoint candidates.
- Primary endpoint remains the existing host/port for backward compatibility.
- One fallback endpoint is editable in the current UI; the model supports a list.
- Storage persists fallback endpoints while retaining the legacy single-profile mirror.
- Terminal transport tries the next endpoint only for retryable NETWORK failures.
- SSH command runner uses the same rule, so Monitoring SSH and Git can follow the same route.
- Host-key TRUST/AUTH failure never causes automatic fallback.
- Every fallback hostname/port has independent host-key verification.
- Terminal status reports the endpoint actually used.
- Terminal credentials are wiped from temporary char arrays after authentication attempt.
- Editing one profile no longer silently removes global trust material for another profile.

## Explicitly deferred to CP12B2

SFTP route parity. File writes must never be replayed across routes after uncertain delivery,
so SFTP fallback requires a connection-phase-only implementation.

## Safety invariants

- no blind host-key inheritance;
- no fallback on auth failure;
- no command replay;
- private key remains in Keystore-backed credential vault;
- RESEARCH_ONLY / no live authority unchanged.
