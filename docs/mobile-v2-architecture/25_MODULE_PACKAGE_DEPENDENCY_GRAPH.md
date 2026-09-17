# Этап 25 — Модульная карта и dependency graph

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Разбить приложение на независимые модули так, чтобы параллельная разработка, targeted tests и change-aware CI были реальными, а не декларативными.

## Предлагаемые Gradle modules

- :app — composition root/navigation only.
- :core:model — общие immutable модели.
- :core:result — ошибки/result types.
- :core:logging — безопасные локальные diagnostics.
- :core:security — credential abstractions/host verification contracts.
- :core:network — network state primitives.
- :core:ui — theme/components/Russian design system.
- :feature:terminal — terminal screen/emulator adapter/input.
- :feature:sessions — workspace/session state machine.
- :feature:connections — connection profiles/enrollment UX.
- :feature:files — SFTP/file browser.
- :feature:editor — code editor.
- :feature:git — Git UI/contracts.
- :feature:atlas — control-plane native UI.
- :feature:ai — ATLAS AI proposal/patch UX.
- :feature:settings — preferences/keyboard profiles.
- :transport:ssh — SSH/PTTY implementation.
- :transport:sftp — SFTP implementation.
- :transport:gateway — HTTPS/WSS RC2 client.
- :storage:local — workspace/preferences/state persistence.
- :testing:fakes — fake terminal/filesystem/gateway/transports.

## Dependency rules

Feature modules depend on interfaces/core, never on another feature implementation directly.

Transport modules implement interfaces exposed by core/domain contracts.

`:app` wires implementations to interfaces via explicit composition root/DI.

Forbidden examples:

- terminal -> concrete gateway implementation;
- editor -> concrete SSH implementation;
- git -> Android Activity;
- transport -> Compose UI.

## Cycles

Gradle dependency cycles are forbidden. Architecture test verifies allowed edges.

## Public API discipline

Каждый модуль имеет минимальный public surface. Internal implementation остаётся internal/private. Это уменьшает accidental coupling и ускоряет incremental compilation.

## Build impact

Изменение keyboard UI не должно перекомпилировать SSH/SFTP/Gateway. Изменение gateway DTO не должно перекомпилировать terminal emulator.

## Parallel tracks

После стабилизации core contracts можно параллельно вести:

Track A: terminal/input.
Track B: ssh/session.
Track C: files/editor/git.
Track D: gateway/control-plane.
Track E: Russian UX/settings.
Track F: testing/fakes.

## Gate

Architecture CI строит module graph и блокирует forbidden dependencies/cycles.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
