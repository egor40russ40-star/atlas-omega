# CP13A — deterministic terminal keyboard

Date: 2026-09-19

## Scope

Professional terminal input foundation after real-device G8 exposed missing Enter/paste and clipped critical keys.

## Changes

- critical row is fixed-width and never horizontally scrolls;
- visible critical keys: ESC, TAB, ENTER, Ctrl-C and four arrows;
- second row has BASIC / SHELL / CODE layers;
- shell layer exposes common Ctrl sequences;
- code layer exposes common programming punctuation;
- deterministic TerminalInputEncoder separates paste from run;
- paste adds no CR/newline;
- run appends exactly one CR after UTF-8 text;
- unit coverage verifies exact byte behavior and presence of critical actions.

## Safety

No hidden execution is introduced. Paste and run remain separate. Multiline run still requires explicit confirmation.

LIVE_TRADING_ENABLED = NO
RESEARCH_ONLY = YES

## Gate

compile + tests + lint + safety + legacy regression.
