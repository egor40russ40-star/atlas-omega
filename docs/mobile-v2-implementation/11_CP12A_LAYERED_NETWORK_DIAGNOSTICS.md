# CP12A — Layered network diagnostics

Date: 2026-09-19

## Field problem

Real-device G8 proved that these failures must not be collapsed into one generic SSH/Gateway error:

- MagicDNS name resolution can fail;
- TCP can reach port 22 while the remote SSH side closes before KEX;
- a public VM endpoint can remain healthy while a Tailnet endpoint is unhealthy;
- credentials are irrelevant until transport/host verification reaches authentication.

## Implemented

A shared transport failure classifier now distinguishes:

- DNS resolution failure;
- route unavailable;
- timeout;
- connection refused;
- remote close/reset before protocol completion;
- TLS/certificate failure;
- unknown transport failure.

SSH terminal, SSH command runner and Gateway use the same taxonomy.

Monitoring now presents:

- human Russian summary;
- layer state;
- suggested next action;
- expandable technical detail.

Raw transport messages are no longer the primary user-facing error.

## Safety

- TLS failure is not bypassed;
- unknown SSH host keys remain blocked;
- no automatic credential change;
- no command replay;
- no live-trading authority.

## Gate

compile + tests + lint + safety + legacy regression.
