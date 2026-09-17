# 37 — Feature Flags, Configuration and Safe Rollout

## Status
FROZEN ARCHITECTURE ADDENDUM

## Goal
Allow controlled activation of new V2 capabilities without turning runtime configuration into an uncontrolled remote-code mechanism.

## Configuration layers
Priority from lowest to highest:
1. build defaults;
2. local persisted user settings;
3. device capability detection;
4. signed/validated server capability response;
5. temporary developer override in non-release builds only.

## Flag classes
### F0 — Visual
UI density, optional indicators, layout experiments.

### F1 — Productivity
Command palette features, editor helpers, non-destructive shortcuts.

### F2 — Transport
Alternative reconnect strategy, protocol optimization, session tuning.

### F3 — Security/Trust
Enrollment, credential, host-identity behavior.

### F4 — Mutating/Backend-sensitive
Anything that can change remote files/jobs/state.

F3/F4 cannot be silently enabled from remote config. They require application version support and explicit local policy.

## Rules
- every flag has an owner, default, expiry/review date and removal plan;
- flags are typed, not free-form strings spread through UI code;
- unknown flags are ignored safely;
- incompatible flags fail closed;
- release builds do not expose arbitrary developer override UI;
- server capability advertisement never grants permissions the client/device identity does not already have.

## Capability negotiation
Client reports supported protocol/features. Server reports supported additive capabilities. Effective capability is intersection:

`effective = client_supported ∩ server_supported ∩ device_authorized`

## Rollout
Candidate rollout sequence:
1. disabled by default;
2. internal/dev activation;
3. targeted real-device test;
4. candidate channel;
5. stable default after acceptance;
6. remove obsolete flag after migration window.

## Kill switch
A narrowly scoped feature may be disabled through validated control-plane configuration when it causes crashes or severe incompatibility. Kill switch cannot enable privileged behavior; only disable/degrade a feature.

## Acceptance
UNTYPED_FLAGS = FORBIDDEN
REMOTE_PERMISSION_GRANT = FORBIDDEN
SECURITY_FLAG_REMOTE_ENABLE = FORBIDDEN
CAPABILITY_INTERSECTION = REQUIRED
KILL_SWITCH_ENABLES_PRIVILEGE = NO
