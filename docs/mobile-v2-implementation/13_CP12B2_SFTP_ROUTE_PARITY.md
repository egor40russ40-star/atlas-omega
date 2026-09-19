# CP12B2 — SFTP route parity without write replay

Date: 2026-09-19

## Goal

Files/editor must use the same approved SSH route candidates as Terminal/Git while preserving
the stronger write-safety rule: an uncertain file operation is never repeated on another route.

## Implemented

- SFTP connection establishment tries ordered profile endpoints.
- Fallback happens only before an SFTP client is established.
- Unknown/changed host key stops immediately for explicit fingerprint verification.
- Authentication failure stops immediately.
- Retryable network failures may advance to the next approved endpoint.
- Once SFTP is established, list/read/write operations run exactly once.
- Operation failure after connection is never automatically replayed on another endpoint.
- SFTP connection failures use the shared layered network diagnostic taxonomy.

## Safety consequence

Atomic write + conflict detection remain unchanged.
A transport break during a file operation is reported to the user rather than guessed/replayed.

## Gate

compile + tests + lint + safety + legacy regression.
