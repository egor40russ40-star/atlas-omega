# Этап 24 — Mobile Coding Workflow Freeze

Статус: ARCHITECTURE FROZEN. Реализация и APK не запускаются без отдельной команды пользователя.

## Зафиксированные подсистемы

1. Programmer keyboard/input model.
2. Workspace/session persistence.
3. Git workflow/change control.
4. ATLAS AI coding assistant integration.
5. Cross-device continuity.
6. Performance/network/power optimization.
7. Productivity automation: command palette/snippets/macros.

## Главный пользовательский сценарий

Открыть приложение -> восстановить workspace -> reconnect SSH -> attach tmux -> терминал готов.

Дальнейший workflow:

Терминал <-> Код <-> Файлы <-> Git <-> ATLAS AI.

Все подсистемы работают вокруг одного workspace context.

## UX invariants

- Terminal First.
- Русский UI по умолчанию.
- Linux/system output остаётся оригинальным.
- SSH setup не занимает главный экран.
- Код/файлы/терминал доступны максимум за 1–2 действия из рабочего экрана.
- Смена Wi-Fi/4G/блокировка экрана не уничтожает удалённые процессы.
- Любое действие AI/macro/snippet, которое может выполнить команду или изменить файл, имеет preview/явное подтверждение согласно risk class.

## Architecture performance targets

- минимальный cold-start path без блокирующего ожидания сети;
- bounded terminal memory;
- event-driven network channels;
- Fast Gate для локальных изменений;
- Full Gate только по необходимости/перед release;
- change-aware CI;
- параллельные workstreams;
- interface-first + fake-first development;
- codegen для повторяющихся контрактов;
- intelligent test/build routing.

## Development critical path

После команды START IMPLEMENTATION порядок остаётся управляемым dependency graph, а не одной длинной цепочкой.

Foundation -> Interfaces -> parallel tracks:

- Terminal/Input;
- SSH/Session;
- Files/Editor;
- Control Plane;
- Russian UX;
- Test infrastructure.

Затем Integration -> Hardening -> Real Device -> APK candidate.

## Release rule

Наличие компилируемого APK не означает готовность.

Минимальные состояния:

ARCHITECTURE_READY
IMPLEMENTATION_READY
INTEGRATION_PASS
REAL_DEVICE_PASS
APK_CANDIDATE
RELEASE_ACCEPTED

Переход к следующему состоянию выполняется только после соответствующего gate.

## Current state

ARCHITECTURE_V2=READY
TERMINAL_FIRST=FROZEN
RUSSIAN_FIRST=FROZEN
AUTOMATION=FROZEN
MOBILE_CODING_WORKFLOW=FROZEN
ANDROID_IMPLEMENTATION=NOT_STARTED
NEW_APK_BUILD=BLOCKED_UNTIL_USER_COMMAND
DEPLOYMENT=NOT_STARTED
LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
