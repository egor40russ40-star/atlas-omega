# Этап 27 — Terminal/session protocol contract

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Зафиксировать границу между terminal UI, session manager и SSH transport.

## TerminalSession interface

Абстракция предоставляет:

- connect(profile, workspace)
- disconnect(reason)
- attach(remoteSessionId)
- resize(cols, rows)
- sendBytes(bytes)
- sendPaste(text, bracketed)
- events(): Flow<TerminalEvent>
- state(): StateFlow<TerminalConnectionState>

UI не знает о SSH socket/client implementation.

## TerminalEvent

- Output(bytes)
- TitleChanged(title)
- WorkingDirectoryHint(path)
- Bell
- RemoteClosed(exitStatus?)
- Reconnected
- Error(typedError)

## SessionManager

SessionManager отвечает за:

- profile resolution;
- trust/auth prerequisite;
- reconnect policy;
- tmux attach/create policy;
- tab<->remote mapping;
- foreground-service lifecycle;
- session event fan-out.

## tmux contract

Workspace имеет стабильный tmux namespace. Создание новой tmux session — отдельное явное решение, а не side-effect каждого reconnect.

Attach flow должен быть idempotent: повторный вызов не запускает повторно пользовательскую команду.

## Resize

Размер PTY вычисляется после layout measurement. Изменения orientation/keyboard height coalesced и отправляются только при изменении rows/cols.

## Input ordering

Byte input сохраняет порядок. UI events не могут обгонять друг друга при concurrent coroutines. Используется single-writer queue на сессию.

## Output ordering

SSH reader -> bounded queue -> terminal emulator. Drop/reorder output запрещены. При backpressure renderer может пропускать промежуточные frames, но emulator получает полный поток.

## Reconnect semantics

Reconnect никогда не replays произвольный пользовательский input. После attach приложение получает текущее состояние удалённой сессии через terminal/tmux behavior.

## Cancellation

Connect/reconnect jobs cancellable. Закрытие вкладки должно явно отличаться от detach:

- Detach: удалённый процесс остаётся.
- Close remote: завершение pane/session после подтверждения.

## Test doubles

FakeTerminalSession умеет сценарии:

- normal output;
- delayed output;
- disconnect/reconnect;
- auth failure;
- host-key change;
- huge output/backpressure;
- remote close.

## Gate

Contract tests обязательны до подключения реального SSH transport к UI.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
