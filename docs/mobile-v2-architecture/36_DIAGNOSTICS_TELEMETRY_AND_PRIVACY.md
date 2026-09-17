# 36 — Diagnostics, Telemetry and Privacy

## Status
FROZEN ARCHITECTURE ADDENDUM

## Goal
Provide enough observability to diagnose mobile/SSH/Gateway/session problems without exposing secrets or making telemetry a runtime dependency.

## Principle
Diagnostics are local-first, privacy-preserving, and non-blocking.

## Diagnostic domains
- app/version/build channel;
- Android version/device class;
- connectivity layer states;
- Gateway health summary;
- SSH session lifecycle events;
- tmux attach/recovery events;
- SFTP/file conflict events;
- performance timings;
- crash/failure categories;
- CI/release compatibility metadata.

## Never collect/export
- private key material;
- passwords/passphrases;
- bearer tokens/session secrets;
- complete shell command history by default;
- arbitrary file contents;
- clipboard contents;
- raw terminal scrollback unless user explicitly selects it for export;
- full sensitive environment variables.

## Redaction
All diagnostic export passes through a redaction pipeline before file creation.
Redaction rules cover:
- known secret fields;
- URI query tokens;
- Authorization headers;
- PEM blocks;
- likely API keys;
- user-configured additional redaction patterns.

## Event model
Structured events use typed categories rather than free-form logs where possible.
Example categories:
- NETWORK_REACHABILITY_CHANGED
- GATEWAY_HEALTH_CHANGED
- SSH_CONNECT_START/PASS/FAIL
- HOST_IDENTITY_CHANGED
- TMUX_ATTACH_PASS/FAIL
- PTY_RESIZE
- SFTP_CONFLICT
- WORKSPACE_RESTORED
- BUILD_COMPATIBILITY_BLOCK

## Local retention
Logs are bounded by size/time. Rotation is mandatory. Diagnostics must never grow without limit.

## Telemetry
Remote telemetry, if ever enabled, is opt-in and must be separable from essential functionality. App operation must remain complete with telemetry disabled.

## Diagnostic bundle
User action `Создать диагностический пакет` produces:
- manifest.json;
- sanitized logs;
- layer-state snapshot;
- app/build/device metadata;
- compatibility summary;
- checksums.

Before export, UI displays exactly what categories will be included.

## Crash handling
Crash recovery must preserve workspace context where safe. Crash report generation must not include secrets or terminal contents by default.

## Acceptance
DIAGNOSTICS_LOCAL_FIRST = YES
TELEMETRY_REQUIRED_FOR_OPERATION = NO
SECRET_EXPORT = FORBIDDEN
LOG_RETENTION_BOUNDED = YES
REDACTION_GATE = REQUIRED
