# ATLAS Mobile 2 — Этап 5. Код, файлы и связь с терминалом

Статус: **ЗАФИКСИРОВАНО**

## 1. Принцип

ATLAS Mobile 2 остаётся terminal-first приложением, но код и файлы должны быть доступны без постоянного переключения в отдельние внешние приложения.

Связь модулей:

```text
Файлы ⇄ Код ⇄ Терминал ⇄ ATLAS
```

Все четыре режима работают с одной выбранной machine/workspace context.

## 2. Workspace

Пользователь выбирает рабочую область, например:

```text
Machine: NucBox
Workspace: ~/ATLAS_EXECUTION_NODE
```

Workspace model:

```text
Workspace
├── id
├── machineProfileId
├── rootPath
├── displayName
├── defaultTerminalSessionId
├── recentFiles
└── permissions/capabilities
```

Пути не хардкодятся в UI.

## 3. Remote file access

Основной transport для файлов — SFTP поверх того же SSH trust boundary.

Интерфейс:

```text
RemoteFileRepository
├── list(path)
├── stat(path)
├── readText(path)
├── writeText(path, content, expectedRevision)
├── mkdir(path)
├── rename(from, to)
├── delete(path)            # с подтверждением
└── search(query, root)
```

Операции записи должны поддерживать optimistic concurrency / revision check, чтобы случайно не затереть файл, изменённый на сервере другой сессией.

## 4. Безопасная запись файла

Для текстового редактора предпочтительна схема:

```text
read + remote revision/hash
        ↓
edit local buffer
        ↓
write temp file
        ↓
fsync/close
        ↓
atomic rename
```

Если исходный файл изменился после открытия:

```text
REMOTE_CHANGED
```

UI предлагает:

- сравнить;
- перезагрузить;
- сохранить копию;
- принудительно перезаписать только отдельным действием.

## 5. Code editor

Первый полноценный editor должен поддерживать:

- UTF-8 text;
- line numbers;
- monospace font;
- syntax highlighting минимум Python / shell / JSON / YAML / Markdown;
- search/replace;
- go-to-line;
- undo/redo;
- indentation;
- spaces/tabs policy;
- autosave локального draft, но не silent remote overwrite;
- large-file guard;
- read-only mode для бинарных/слишком больших файлов.

## 6. Terminal bridge

Ключевой сценарий:

```text
выделить код/команду
        ↓
▶ Выполнить в терминале
        ↓
выбрать active session
        ↓
отправить текст в PTY
```

По умолчанию приложение **не добавляет Enter автоматически**, если пользователь не выбрал действие `Выполнить`. Для действия `Вставить в терминал` текст только вставляется.

Два разных действия:

```text
Вставить → bytes без Enter
Выполнить → bytes + Enter после подтверждённого выбора
```

## 7. Path:line bridge

Terminal renderer распознаёт безопасные текстовые шаблоны вида:

```text
path/to/file.py:123
path/to/file.py:123:45
```

По нажатию приложение предлагает открыть файл в editor на строке 123.

Автоматическое открытие без действия пользователя не выполняется.

## 8. Git integration

Первый слой Git не заменяет CLI, а ускоряет навигацию:

- status;
- diff текущего файла;
- diff workspace;
- branch name;
- modified/untracked badges;
- открыть файл из diff.

Commit/push могут оставаться terminal-first, пока отдельный безопасный Git UI не будет спроектирован.

## 9. File tree UX

На телефоне:

```text
Файлы
├── быстрый поиск
├── breadcrumbs
├── избранные папки
├── recent files
└── дерево текущего уровня
```

Не отображать всё рекурсивное дерево огромного проекта сразу. Подгружать уровни лениво.

## 10. Split mode

В landscape/tablet:

```text
┌──────────────┬────────────────────┐
│ Файлы        │ Код                │
│              │                    │
│              ├────────────────────┤
│              │ Терминал           │
└──────────────┴────────────────────┘
```

На телефоне portrait:

```text
Код ⇄ Терминал ⇄ Файлы
```

быстрое переключение без уничтожения состояния каждого экрана.

## 11. Local drafts

Несохранённый текст editor хранится в локальном encrypted/private app storage как draft metadata/content.

Draft:

- не отправляется в облако;
- переживает Activity/process recreation;
- маркируется machine/workspace/path;
- после успешного remote save удаляется или архивируется ограниченно.

## 12. Large/binary files

Для файлов выше заданного safe threshold editor сначала показывает metadata и предлагает:

- открыть read-only;
- скачать локальную копию;
- открыть через terminal tool.

Бинарные файлы не декодируются как UTF-8 автоматически.

## 13. Search

Архитектура предусматривает два режима:

1. filename search через SFTP/file index;
2. content search через server-side безопасную команду/agent API, предпочтительно `rg`, если доступно.

Поиск не должен скачивать весь workspace на телефон.

## 14. Machine context

Верхняя строка всех dev-экранов показывает текущий контекст:

```text
NucBox / ATLAS_EXECUTION_NODE
```

Это снижает риск редактирования файла не на той машине.

## 15. Delete/rename safety

- destructive actions требуют явного подтверждения;
- корень workspace нельзя удалить из UI;
- системные пути вне разрешённого workspace показываются как advanced access;
- delete не связан с terminal `rm` и не маскирует его — terminal остаётся обычным shell.

## 16. Архитектурный приоритет реализации

Порядок реализации после разрешения пользователя:

1. Terminal core.
2. Stable session/tmux.
3. Remote file tree/read.
4. Text editor/save with conflict protection.
5. Terminal bridge.
6. Git read UI.

То есть editor не должен задерживать выпуск стабильного terminal core, но его интерфейсы определены заранее.

**ARCHITECTURE_STAGE_5 = COMPLETE**
