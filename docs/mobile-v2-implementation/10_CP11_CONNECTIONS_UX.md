# CP11 — Connections UX

Date: 2026-09-19

## Goal

Expose the CP10 multi-profile registry in the real Android UI without losing the safe
credential/trust model.

## Implemented

- Connections now opens a real profile list instead of jumping directly into one edit form.
- Active profile is marked.
- Add creates an unsaved profile draft with a unique id.
- Back from an unsaved draft restores the previously persisted active profile.
- Edit/select changes machine context and resets Files/Editor/Git/Gateway transient state.
- Connect selects the profile, detaches any prior terminal transport, switches to Terminal,
  and starts the normal host-key/auth flow.
- UNENROLLED profiles may connect so the app can observe and ask the user to verify a host key.
- REVOKED profiles remain blocked.
- Credential status is refreshed per profile from Android Keystore.
- Credentials are never copied between profiles.

## Safety

- profile storage contains no password/private key;
- host trust is still explicit;
- switching profiles does not replay a command;
- existing tmux session is detached rather than killed;
- LIVE authority remains absent.

## Gate

Compile + tests + lint + safety + legacy regression must all pass before CP11 checkpoint branch.
