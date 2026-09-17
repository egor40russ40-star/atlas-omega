# G3D — Secure Storage + Connection UX

## Functional changes
- ConnectionProfile remains secret-free.
- MutableCredentialVault added for explicit secret save/remove operations.
- SSH password/private-key material is encrypted at rest with an AES-256-GCM Android Keystore key.
- Credential binary codec supports Russian passwords and private keys without repository/runtime logging.
- Decrypted intermediate byte arrays are zeroed after use where practical.
- Host-key fingerprints are stored separately as non-secret pins.
- Connection list moved into a dedicated Russian UI surface; the main terminal no longer needs connection form fields.
- Trusted profiles can be launched directly; pending/untrusted profiles cannot connect from the normal action.

## Design direction
The daily flow becomes:
`launch -> workspace -> terminal`, not `launch -> fill SSH form -> connect`.
Connection editing/enrollment is an exceptional setup flow.

## Backup rule
The final app manifest/backup rules must exclude `atlas_v2_secret_credentials`; device trust and credentials are never restored from ordinary app backup.

## Safety
LIVE_TRADING_ENABLED = NO
LIVE_TRADING_AUTHORITY = ABSENT
AUTO_TRUST_NEW_DEVICE = NO
RESEARCH_ONLY = YES
APK_BUILD = BLOCKED UNTIL G7
