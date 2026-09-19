# CP13B — terminal resize, safe IME and context paste

Date: 2026-09-19

## Goal

Synchronize the real remote PTY with the dynamically sized termlib terminal and remove
device-specific soft-keyboard ambiguity discovered during G8.

## Implemented

- termlib TerminalEmulator onResize is wired directly to SSH PTY resize;
- remote columns/rows now follow the exact dimensions calculated by termlib after
  orientation, window and keyboard-layout changes;
- raw Terminal keeps hardware-keyboard handling enabled;
- raw terminal soft IME is disabled so Android IME text goes through the explicit
  command field instead of competing with the terminal input bridge;
- terminal context-menu paste is redirected into the safe command draft;
- context paste does not execute anything;
- the same draft is shared by explicit Paste and terminal paste requests.

## Existing upstream capabilities deliberately reused

termlib 0.1.0 already provides text selection, copy UI, dynamic local resize,
pinch zoom and hardware-keyboard handling. ATLAS now bridges its dynamic resize
callback to the remote PTY rather than reimplementing terminal geometry.

## Safety

No command replay and no automatic paste execution are introduced.

LIVE_TRADING_ENABLED = NO
RESEARCH_ONLY = YES

## Gate

compile + tests + lint + safety + legacy regression.
