# Этап 21 — Continuity: телефон ↔ NucBox ↔ физический PC

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Пользователь должен иметь возможность начать работу на телефоне, продолжить на ПК и вернуться обратно без ручного восстановления terminal session, каталога и контекста.

## Принцип

Удалённое состояние является источником истины для процессов и файлов. Телефон и ПК — клиенты одного workspace.

## Shared workspace identity

Workspace имеет устойчивый id и remote metadata:

- machine id;
- project root;
- tmux session id;
- active branch;
- optional shared cursor/file metadata;
- last known test status;
- lease/version для UI-state sync.

Секреты не синхронизируются.

## Terminal continuity

Телефон подключается к той же tmux session, которая доступна с ПК. Новый клиент не должен создавать дубликат процесса без явного запроса.

Поддерживаются два режима:

1. MIRROR — два клиента видят одну tmux pane.
2. HANDOFF — новый клиент становится primary input, предыдущий остаётся read-only или отключает ввод.

По умолчанию для мобильного coding используется HANDOFF, чтобы исключить одновременный ввод с двух устройств.

## Editor continuity

Открытые файлы и cursor positions могут синхронизироваться как best-effort metadata. Источник истины для содержимого файла — remote filesystem + version/hash checks.

## Conflict model

Если файл изменён на другом устройстве после открытия на телефоне:

- silent overwrite запрещён;
- показывается remote/local diff;
- пользователь выбирает reload/merge/save-as/force only with explicit confirmation.

## Presence

Workspace показывает активные клиенты:

- Телефон;
- PC;
- браузер/другой клиент в будущем.

Presence не является security trust — это только UX-информация.

## Offline handoff

Если телефон ушёл offline, tmux и процессы продолжают работать. ПК может подключиться к тому же workspace без ожидания телефона.

## Test continuity

Результаты тестов сохраняют привязку к repository/worktree fingerprint. Другой клиент видит, к какому состоянию кода относится PASS/FAIL.

## Gate

Acceptance: запустить процесс на телефоне, отключить телефон, подключиться с ПК, продолжить работу, затем вернуть телефон к той же сессии без повторного запуска процесса.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
