# ATLAS Mobile 2 — Этап 8. Testing и Acceptance Architecture

Статус: **ЗАФИКСИРОВАНО**

## 1. Принцип

Новая APK не считается готовой только потому, что она компилируется и запускается.

Готовность разделяется на уровни:

```text
SOURCE_VALID
BUILD_VALID
STATIC_VALID
UNIT_VALID
INTEGRATION_VALID
EMULATOR_VALID
REAL_DEVICE_VALID
END_TO_END_VALID
```

Только последний набор допускает статус `READY_FOR_DAILY_USE`.

## 2. CI gates

Минимальный CI pipeline:

```text
1. dependency/toolchain validation
2. static safety gates
3. compile
4. unit tests
5. lint
6. integration tests
7. APK assemble
8. artifact integrity
9. checksum
10. optional emulator tests
```

Любой обязательный gate = FAIL → артефакт не маркируется как release candidate.

## 3. Static safety gates

CI проверяет минимум:

- отсутствуют приватные ключи/пароли/token literals;
- отсутствует cleartext Gateway URL;
- отсутствует `acceptAllHostKeys`-подобная логика;
- `LIVE_TRADING_ENABLED = false`;
- `RESEARCH_ONLY = true`;
- package id новой версии не конфликтует случайно со старым, пока не принято решение о migration;
- русский resources bundle присутствует;
- terminal не реализован через WebView;
- release build не содержит debug-only credential fixtures.

## 4. Unit tests

Обязательные домены:

### Connection state machine

- валидные переходы;
- invalid transitions blocked;
- `READY` только после полного transport/PTY state;
- reconnect flow;
- host-key changed flow;
- auth failure.

### Terminal keys

- ESC/TAB;
- arrows;
- CTRL A-Z;
- modifier latch/lock;
- UTF-8 text.

### URI/endpoint validation

- HTTPS accepted;
- HTTP rejected;
- malformed endpoint rejected;
- host allow/profile rules.

### Session naming

- tmux-safe session name;
- отсутствие shell injection;
- stable reconnect mapping.

### Storage/security

- secrets не сериализуются в profile model;
- credential reference без raw private key;
- sanitization logs.

## 5. SSH integration tests

В CI поднимается одноразовый тестовый SSH server/container.

Проверяются:

- key authentication;
- host-key verification;
- wrong host key blocked;
- PTY allocation;
- `xterm-256color`;
- window resize;
- stdout/stderr;
- disconnect/reconnect;
- tmux attach, если tmux доступен в test image;
- SFTP list/read/write-temp/rename.

Test server не использует production credentials.

## 6. Terminal renderer tests

Тестовые sequences:

- ANSI colors;
- cursor movement;
- clear screen;
- alternate screen;
- Unicode;
- wide characters;
- long lines;
- high-volume output;
- resize during output;
- selection/scrollback.

## 7. Compose/UI tests

Минимум:

- первый запуск на русском;
- onboarding;
- terminal-first home после onboarding;
- connection state indicators;
- tab creation/switch/close;
- keyboard panel;
- error + technical details;
- settings;
- portrait/landscape;
- system font scaling;
- dark theme baseline.

## 8. Emulator matrix

Минимальный набор перед real-device:

- Android 12 class environment;
- текущий target-level emulator;
- portrait;
- landscape;
- small/medium phone dimensions.

Цель — ловить lifecycle/layout incompatibilities, а не имитировать сетевую специфику реального tailnet.

## 9. Real-device acceptance

На реальном телефоне обязательны следующие сценарии.

### A. Установка/обновление

- APK устанавливается;
- запускается без crash;
- старый клиент не повреждается до принятой migration policy.

### B. Русификация

- все штатные экраны на русском;
- нет английских пользовательских строк кроме технических терминов;
- длинные русские подписи не обрезают критические кнопки.

### C. Терминал

- подключение к доверенной машине;
- shell prompt;
- `pwd`, `ls`, `git status`;
- запуск Python;
- работа `vim` или `nano`;
- `tmux`;
- CTRL+C;
- TAB completion;
- arrows/history;
- кириллица в текстовом вводе при поддерживаемой remote locale;
- paste многострочного текста.

### D. Живучесть

- свернуть приложение на 5 минут;
- заблокировать экран;
- вернуть приложение;
- сменить Wi-Fi ↔ mobile data при активном Tailscale;
- кратко потерять сеть;
- восстановить сеть;
- reconnect к той же tmux session;
- удалённый процесс продолжает работать.

### E. Несколько вкладок

- минимум 3 активные terminal tabs;
- разные cwd/processes;
- переключение без смешивания buffers;
- disconnect одной вкладки не ломает остальные.

### F. Host security

- unknown host требует trust;
- known host подключается без повторного вопроса;
- simulated host-key mismatch блокирует соединение.

## 10. Coding acceptance

Практический тест вместо только синтетических checks:

1. открыть workspace;
2. открыть/создать тестовый `.py` файл;
3. изменить код;
4. сохранить;
5. запустить из terminal;
6. получить ошибку `path:line`;
7. открыть строку ошибки;
8. исправить;
9. повторно запустить;
10. `git diff` показывает ожидаемое изменение.

Этот сценарий считается обязательным, когда editor входит в конкретный milestone.

## 11. Stress tests

Перед статусом daily-use:

- terminal session 60+ минут;
- большой stdout (не менее десятков тысяч строк);
- многократные resize;
- 20+ reconnect cycles в controlled test;
- 4 tabs;
- repeated background/foreground;
- file browser на большом workspace;
- проверка памяти/утечек.

## 12. Performance targets

Цели, а не обещания до измерений:

- UI не блокируется network I/O;
- terminal input echo субъективно мгновенный на нормальном tailnet;
- reconnect state появляется сразу, без зависшего `ONLINE`;
- 4 типовых terminal tabs не приводят к OOM;
- scrollback не вызывает длительных main-thread stalls.

Фактические значения фиксируются benchmark/evidence перед RC.

## 13. Failure injection

Тестируется намеренно:

- DNS unavailable;
- Tailscale unavailable;
- port closed;
- auth rejected;
- host key changed;
- server closes SSH;
- Gateway HTTP 5xx;
- process recreation;
- storage read failure;
- corrupted local session metadata.

Приложение должно переходить в объяснимое состояние, а не зависать.

## 14. Evidence

Каждый milestone сохраняет:

```text
commit SHA
build run id
APK SHA-256
unit/lint/integration results
supported Android level
real-device checklist
known limitations
safety invariants
```

## 15. Release states

```text
DEV_BUILD
INTERNAL_ALPHA
REAL_DEVICE_ALPHA
BETA
RC
READY_FOR_DAILY_USE
```

`INTERNAL_ALPHA` не называется «готовой» только на основании CI.

## 16. APK creation gate

Даже при полностью готовой архитектуре APK implementation/build не начинается без отдельной команды пользователя.

**ARCHITECTURE_STAGE_8 = COMPLETE**
