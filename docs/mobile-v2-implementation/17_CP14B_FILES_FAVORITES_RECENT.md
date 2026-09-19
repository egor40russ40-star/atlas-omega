# CP14B — Files favorites + recent

Date: 2026-09-19

## Scope

Complete the fast-navigation layer for Files without weakening the workspace boundary.

## Implemented

- per-profile favorite directories;
- per-profile recent files;
- compact horizontal shortcut rows;
- one-tap favorite toggle for the current directory;
- recent files update only after a successful remote read;
- stale/out-of-workspace recent paths are removed instead of opened;
- favorites/recent are navigation hints only and contain no credentials;
- every shortcut is revalidated by WorkspacePathPolicy before SFTP use;
- bounded lists prevent unbounded SharedPreferences growth;
- pure policy tests cover favorite limits and recent ordering/deduplication.

## Safety

Favorites and recents cannot bypass lexical or canonical SFTP workspace enforcement.

LIVE_TRADING_ENABLED = NO
RESEARCH_ONLY = YES

## Gate

compile + tests + lint + safety + legacy regression.
