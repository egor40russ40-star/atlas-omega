# CP15A — Editor history + search foundation

Date: 2026-09-19

## Implemented

- bounded deterministic undo/redo history;
- redo branch is dropped after a new edit;
- dirty state compares against the last successfully loaded/saved remote text;
- save keeps undo history while resetting the dirty baseline;
- exact / case-insensitive search count;
- line count;
- search and history policies are pure and unit-tested;
- no extra editor dependency was introduced.

## Safety

Remote saving still uses conflict detection + atomic SFTP replacement.
Undo/redo only changes the local draft until the user explicitly saves.
Terminal execution remains explicit.

LIVE_TRADING_ENABLED = NO
RESEARCH_ONLY = YES

## Next

CP15B: selection-aware search navigation / line-number presentation / conflict UX.

## Gate

compile + tests + lint + safety + legacy regression.
