# G3A — Design System + Terminal Foundation

## Implemented
- Russian-first dark ATLAS design system foundation.
- Shared dimensions/status semantics.
- Full-screen terminal chrome contract.
- Two-row programmer keyboard foundation.
- ANSI key encoder and CTRL mappings.
- Multi-line paste safety classification.
- Transport-independent TerminalSessionPort.
- Delivery certainty explicitly represents ambiguous writes so reconnect logic cannot silently resend commands.

## Design direction
Terminal surface remains visually dominant. Connection setup is not part of the main terminal canvas. Status is compact and functional, with code/files/Git/ATLAS navigation intended to stay one action away.

## CI optimization
Implementation runs now use concurrency cancellation so stale commits do not consume full CI time.

## Safety
LIVE_TRADING_ENABLED = NO
LIVE_TRADING_AUTHORITY = ABSENT
RESEARCH_ONLY = YES
APK_BUILD = BLOCKED UNTIL G7
