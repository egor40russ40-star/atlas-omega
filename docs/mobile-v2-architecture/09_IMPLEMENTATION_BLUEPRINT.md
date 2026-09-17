# ATLAS Mobile 2 — Этап 9. Implementation Blueprint

Статус: **ЗАФИКСИРОВАНО**

Этот документ определяет порядок будущей реализации. Он не является разрешением на сборку APK.

## 1. Главное правило

Новая версия не строится одним большим `MainActivity.kt`.

Каждый слой вводится отдельно, проходит свои тесты и только затем становится зависимостью следующего слоя.

## 2. Целевая package structure

```text
omega.atlas.mobile.v2
│
├── app
│   ├── AtlasApplication
│   ├── MainActivity
│   ├── AppNavigation
│   └── AppState
│
├── core
│   ├── model
│   ├── result
│   ├── logging
│   ├── network
│   ├── security
│   ├── storage
│   └── localization
│
├── connections
│   ├── model
│   ├── enrollment
│   ├── profiles
│   └── ui
│
├── terminal
│   ├── emulator
│   ├── transport
│   │   ├── TerminalTransport
│   │   └── ssh
│   ├── session
│   │   ├── TerminalSession
│   │   ├── TerminalSessionManager
│   │   └── TerminalSessionService
│   ├── tmux
│   ├── input
│   ├── scrollback
│   └── ui
│
├── files
│   ├── model
│   ├── remote
│   ├── cache
│   └── ui
│
├── code
│   ├── model
│   ├── editor
│   ├── terminalbridge
│   └── ui
│
├── atlas
│   ├── api
│   ├── machines
│   ├── jobs
│   ├── health
│   └── ui
│
└── settings
    └── ui
```

## 3. Dependency direction

```text
UI → domain/controller interfaces → repositories/services → transport/storage
```

Запрещено:

```text
Composable → raw SSH socket
Composable → private key
Composable → SharedPreferences secret
WebView → terminal session
```

## 4. Phase A — Foundation

Реализуется без network login:

- package migration to `.v2`;
- resources/i18n;
- AppNavigation;
- theme;
- core models/results;
- structured sanitized logging;
- test skeleton.

Gate A:

```text
compile PASS
unit PASS
lint PASS
Russian UI resources PASS
```

## 5. Phase B — Terminal Emulator + Input

Без production SSH:

- termlib adapter;
- terminal canvas;
- special keyboard;
- modifier state;
- resize calculations;
- scrollback/search;
- font gestures;
- fake/local byte transport for tests.

Gate B:

- ANSI rendering tests;
- key sequences tests;
- portrait/landscape UI tests;
- large output test.

## 6. Phase C — SSH Transport

- `TerminalTransport` interface;
- SSH implementation;
- strict host key verification;
- key authentication;
- PTY open/resize;
- SFTP transport base;
- sanitized errors.

Gate C:

- ephemeral SSH integration server;
- host-key mismatch blocked;
- key auth PASS;
- PTY PASS;
- resize PASS.

## 7. Phase D — Session Service + tmux

- Foreground Service;
- multi-session manager;
- session metadata persistence;
- reconnect policy;
- tmux attach/create;
- notification;
- lifecycle recovery.

Gate D:

- 3+ simultaneous sessions;
- background/foreground;
- controlled disconnect/reconnect;
- same tmux resumed;
- no duplicate command replay.

## 8. Phase E — Managed Connections

- device identity;
- secure credential vault;
- profile repository;
- onboarding;
- machine selection;
- manual advanced profile fallback.

Gate E:

- no secret in ordinary storage/logs;
- trust required;
- revoke/rotation paths testable;
- normal daily flow has no repetitive host/user/key form.

## 9. Phase F — Terminal-First UI freeze

Только после A-E собирается целевой daily terminal UI:

```text
header machine/session
full terminal
compact programmable key rows
bottom navigation
```

Gate F:

- пользователь от app icon до typing-ready terminal проходит автоматически/в одно действие после onboarding;
- terminal занимает основную площадь экрана;
- формы подключения отсутствуют на основном terminal screen.

## 10. Phase G — Files

- SFTP repository;
- lazy file browser;
- text read;
- safe write/atomic rename;
- conflict detection;
- recent/favorites.

Gate G:

- write conflict не приводит к silent overwrite;
- large/binary guard;
- workspace boundary visible.

## 11. Phase H — Code

- editor;
- syntax highlighting;
- search/replace;
- line navigation;
- local draft;
- `path:line` bridge;
- `Вставить`/`Выполнить` terminal bridge.

Gate H:

- coding acceptance scenario полностью PASS.

## 12. Phase I — Native ATLAS Control

- version;
- machines;
- health;
- jobs;
- capabilities;
- diagnostics.

Legacy WebView остаётся только временным compatibility fallback, если конкретная функция ещё не портирована.

Gate I:

- старый RC2 E2E PASS;
- новый API additive;
- failure isolation PASS.

## 13. Phase J — Hardening

- stress;
- memory profiling;
- reconnect loops;
- error injection;
- accessibility;
- localization audit;
- dependency/security scan;
- real-device certification.

## 14. Build artifact policy

Каждый installable artifact содержит metadata:

```text
version
commit SHA
branch
build run
APK SHA-256
build type
architecture stage version
known limitations
```

Нельзя выдавать `alpha` за `ready for daily use`.

## 15. Migration from alpha1

`0.2.0-alpha1` рассматривается как прототип, подтверждающий:

- Compose build pipeline;
- terminal emulator library compatibility;
- SSH library compatibility;
- APK installability;
- русский UI feasibility.

Его UI/сессионная архитектура не переносится как монолит. Полезные адаптеры могут быть переиспользованы после проверки интерфейсов.

## 16. Rollback

До real-device acceptance новой версии:

- alpha1/старый клиент не удаляются автоматически;
- backend RC2 rollback сохраняется;
- implementation branch отделён от architecture freeze;
- каждый backend change additive и обратим.

## 17. Оптимизация разработки

Чтобы не тратить время на повторные инфраструктурные ошибки:

- toolchain фиксируется заранее;
- Gradle/SDK/Compose compatibility матрица закрепляется в CI;
- dependencies кешируются;
- compile/unit выполняются раньше lint/emulator;
- UI screenshot/instrumentation идут после быстрых gates;
- artifact создаётся только после обязательных gates.

## 18. Разрешение на начало реализации

После архитектурного freeze следующий шаг — **ожидание команды пользователя**.

Без этой команды:

- app source не переписывается;
- новая APK не собирается;
- backend не модифицируется;
- deployment не выполняется.

**ARCHITECTURE_STAGE_9 = COMPLETE**
