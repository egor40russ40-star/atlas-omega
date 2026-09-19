# CP14A — Files workspace boundary + navigation

Date: 2026-09-19

## Scope

Make Files safe and usable across NucBox/Cloud VM profiles.

## Implemented

- lexical WorkspacePathPolicy blocks navigation above the active profile workspace;
- parent navigation clamps at workspace root;
- file open/save checks the active workspace boundary;
- SFTP performs a second server-side canonicalPath check;
- symlink/canonical-path escape outside the workspace is blocked before read/write/list;
- hidden files are off by default with an explicit toggle;
- breadcrumb chips navigate within the workspace;
- the parent button stops at the profile root;
- boundary failure has a Russian user-facing error;
- unit tests cover path normalization and traversal rejection.

## Defense in depth

UI/runtime lexical policy prevents accidental traversal.
SFTP canonical-path policy prevents a symlink from turning an apparently safe path
into an out-of-workspace server path.

LIVE_TRADING_ENABLED = NO
RESEARCH_ONLY = YES

## Gate

compile + tests + lint + safety + legacy regression.
