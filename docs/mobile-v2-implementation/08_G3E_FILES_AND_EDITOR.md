# G3E — Files + Editor Foundation

## Implemented
- Transport-independent RemoteFilesPort for directory listing, text reads and atomic writes.
- Remote file snapshots carried through edits for optimistic conflict control.
- FileConflictGuard prefers content hashes and falls back to size+mtime when hashes are unavailable.
- Mobile code editor foundation uses monospaced text and keeps Save / Insert into terminal / Run in terminal as separate actions.
- Traceback parser turns Python `File ..., line N` and generic `path:line:column` output into editor locations.

## Safety semantics
- A remote file changed since it was opened must not be silently overwritten.
- INSERT never adds implicit execution.
- RUN is a distinct explicit action and later integrates with paste/run confirmation policy.
- Actual SFTP adapter is intentionally deferred until these contracts pass Fast Gate.

## Design direction
Code stays one action away from Terminal. Terminal remains primary; editor is optimized for quick changes, traceback jumps and immediate return to the same remote tmux workspace.

## Safety
LIVE_TRADING_ENABLED = NO
LIVE_TRADING_AUTHORITY = ABSENT
RESEARCH_ONLY = YES
APK_BUILD = BLOCKED UNTIL G7
