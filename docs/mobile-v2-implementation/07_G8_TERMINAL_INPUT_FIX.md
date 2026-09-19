# G8 — Terminal input blocking fix

Date: 2026-09-19

## Field finding

Real-device G8 reached READY on the Cloud VM through SSH + PTY + tmux, but terminal input UX was blocking:

- no visible Enter control;
- no explicit Paste control;
- system IME interaction with the terminal view was not reliable enough for primary input;
- previous command entry could appear concatenated/interleaved, so user input must have one deterministic send path.

## Fix

The terminal now has a dedicated Compose input bar:

- editable command/text field;
- explicit **Вставить** button that copies clipboard text into the field without executing it;
- explicit **Enter** button for raw CR;
- explicit **Отправить** button that sends text + Enter as one byte payload, preserving order;
- Android IME Send uses the same deterministic path;
- multiline text requires confirmation before text + Enter are transmitted;
- programmer keyboard exposes **ENTER** in the first critical row.

This follows the frozen input rule: paste and run are separate actions.

## Safety

- no command is executed by pressing **Вставить**;
- multiline run requires an explicit confirmation;
- live-trading authority remains absent;
- RESEARCH_ONLY remains enabled.

## Gate

Required before the next APK candidate:

1. compile app-v2;
2. terminal unit tests including exact CR byte for ENTER;
3. lint;
4. legacy RC regression;
5. real-device retest against Cloud VM.
