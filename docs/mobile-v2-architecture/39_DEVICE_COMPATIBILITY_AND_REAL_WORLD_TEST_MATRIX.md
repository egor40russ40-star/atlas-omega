# 39 — Device Compatibility and Real-World Test Matrix

## Status
FROZEN ARCHITECTURE ADDENDUM

## Goal
Prevent a green emulator/CI build from being treated as proof that the mobile coding experience works on real Android devices.

## Supported platform baseline
- minSdk remains explicit in build architecture;
- target/compile SDK may advance independently under compatibility gates;
- primary real-device certification must include the user's actual Android device class;
- phone and tablet layouts are tested separately where available.

## Test dimensions
### Android versions
At minimum:
- minimum-supported API representative;
- current primary user API representative;
- latest stable supported API.

### Form factors
- compact phone;
- standard phone;
- large phone;
- tablet/large screen when supported.

### Orientation
- portrait;
- landscape;
- rotation while terminal/session is active.

### Input
- Gboard-like soft keyboard;
- OEM keyboard representative;
- physical Bluetooth/USB keyboard;
- clipboard paste;
- long press selection;
- hardware ESC/TAB/arrows/modifiers.

### Network transitions
- Wi-Fi steady;
- mobile data steady;
- Wi-Fi → mobile data;
- mobile data → Wi-Fi;
- temporary packet loss;
- Tailscale unavailable/recovered;
- screen lock/unlock during active tmux session.

### Lifecycle
- foreground/background;
- process recreation;
- system memory pressure;
- app force-stop followed by relaunch;
- device reboot followed by reconnect.

### Terminal workloads
- high-output command;
- interactive shell;
- vim-like full-screen app;
- tmux attach/detach;
- git diff with long output;
- pytest/build output;
- Unicode/Cyrillic paths/text;
- ANSI colors and cursor movement.

## Device capability profile
At runtime the app records non-sensitive capability facts such as:
- API level;
- screen class;
- physical keyboard presence;
- memory class;
- supported biometric/keystore capabilities if relevant to local credential protection.

Capability facts may tune UI/performance but may not weaken trust/security invariants.

## Real-device release gate
A candidate cannot reach FINAL_ACCEPTANCE from emulator/CI alone.
Mandatory real-device checklist includes:
- install/upgrade;
- enrollment;
- terminal connection;
- tmux persistence;
- keyboard shortcuts;
- rotate/background/reconnect;
- SFTP file open/save/conflict;
- Git diff/status;
- Russian UI review;
- diagnostic bundle;
- battery/thermal sanity during sustained terminal use.

## Evidence
Record test build SHA/version, device class/API, test outcomes, timestamps and known deviations. Do not collect sensitive device identifiers unless strictly required.

## Acceptance
EMULATOR_ONLY_RELEASE = FORBIDDEN
REAL_DEVICE_CERTIFICATION = REQUIRED
NETWORK_TRANSITION_TESTS = REQUIRED
PHYSICAL_KEYBOARD_TEST = REQUIRED
RUSSIAN_UI_REAL_DEVICE_REVIEW = REQUIRED
