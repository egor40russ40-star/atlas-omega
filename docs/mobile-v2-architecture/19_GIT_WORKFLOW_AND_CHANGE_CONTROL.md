# Этап 19 — Git workflow и контроль изменений

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Дать мобильному пользователю безопасный контроль над кодом без необходимости каждый раз вводить длинные git-команды вручную.

## Режимы Git

### Read operations

По умолчанию доступны безопасные операции:

- status;
- diff;
- log;
- branch list;
- show file history;
- blame selected line;
- staged/unstaged overview.

### Write operations

Операции, изменяющие repository state, требуют явного действия:

- stage/unstage;
- commit;
- checkout/switch;
- pull/rebase;
- merge;
- push.

Опасные операции (`reset --hard`, force push, destructive clean) не выводятся как обычные быстрые действия и требуют отдельного подтверждения.

## Diff-first workflow

Перед commit приложение показывает:

1. изменённые файлы;
2. staged diff;
3. unstaged diff;
4. возможные generated/binary files;
5. текущую branch;
6. результат быстрых тестов, если они доступны.

## Commit flow

Коммит из мобильного UI:

- пользователь выбирает файлы/hunks;
- приложение формирует staged set;
- показывает финальный diff;
- пользователь вводит сообщение;
- commit выполняется удалённо;
- результат и SHA показываются явно.

## Terminal interop

Любое Git действие можно открыть как команду в terminal preview. UI не должен скрывать, что именно будет выполнено.

## Conflict handling

При merge/rebase conflict приложение переходит в режим конфликтов:

- список конфликтных файлов;
- base/ours/theirs;
- переход к строке;
- разрешение через редактор;
- продолжение только после проверки отсутствия conflict markers.

## Branch safety

Branch, используемая для стабильного backend/runtime, визуально маркируется как protected context. Мобильный клиент не должен автоматически переключать такие ветки.

## Git + тесты

После изменения файлов можно запускать change-aware Fast Gate. Результат привязывается к current working tree hash, чтобы старый зелёный тест не воспринимался как тест текущего кода.

## Gate

Acceptance: status/diff/stage/commit/branch switch/conflict resolution должны работать без потери данных и без скрытых destructive actions.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
