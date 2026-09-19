# CP15B — Editor search navigation + conflict UX

Date: 2026-09-19

## Implemented

- editor uses TextFieldValue so search results can select exact ranges;
- previous/next search wraps deterministically;
- search selection does not modify file content;
- visible cursor line/column;
- remote-change conflict is a first-class editor state;
- save is disabled while a remote conflict is unresolved;
- server reload requires explicit confirmation before discarding the local draft;
- cancelled reload preserves the local draft.

## Safety

A conflicting remote file is never overwritten automatically.
Search/navigation never performs remote writes.
Reload is explicit and destructive only after confirmation.

LIVE_TRADING_ENABLED = NO
RESEARCH_ONLY = YES

## Gate

compile + tests + lint + safety + legacy regression.
