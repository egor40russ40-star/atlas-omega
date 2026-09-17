# G3B — Secure SSH Transport

## Implemented
- CredentialVault contract: secrets are requested by reference, never embedded in ConnectionProfile.
- Explicit host-key pinning policy with UNSEEN / TRUSTED / CHANGED states.
- No TOFU auto-accept in transport.
- Trilead SSH adapter for direct Tailscale/SSH PTY.
- xterm-256color PTY and resize support.
- stdin serialization and typed delivery-unknown failure: reconnect must not silently re-send.
- output streaming through TerminalSessionPort.Listener.
- explicit detach that leaves remote tmux lifecycle to the session layer.
- guarded remote tmux close with strict session-name validation.

## Security direction
The transport can observe an unseen host key, but only an explicit enrollment action may pin it. Credential persistence is intentionally outside the transport and will be backed by Android Keystore in the storage/security lane.

## Safety
LIVE_TRADING_ENABLED = NO
LIVE_TRADING_AUTHORITY = ABSENT
AUTO_TRUST_NEW_DEVICE = NO
RESEARCH_ONLY = YES
APK_BUILD = BLOCKED UNTIL G7
