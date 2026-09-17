# Этап 18 — Workspaces, контекст и сохранение сессий

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Пользователь должен продолжать работу после блокировки экрана, смены сети, перезапуска приложения и перехода телефон ↔ ПК без ручного восстановления каталогов, файлов и терминальных окон.

## Workspace

Workspace — логическая рабочая среда, содержащая:

- machine id;
- project root;
- набор terminal tabs;
- tmux session/window/pane mapping;
- открытые файлы и позиции курсора;
- выбранный Git branch;
- последний активный экран;
- layout терминал/код/файлы;
- keyboard profile;
- безопасные UI preferences.

Секреты и приватные ключи в workspace state не хранятся.

## Persisted state

Локально сохраняется только декларативное состояние UI и идентификаторы удалённых ресурсов. Shell-процессы живут удалённо в tmux.

После cold start:

1. загрузить последний workspace;
2. проверить достижимость машины;
3. восстановить control-plane status;
4. восстановить SSH;
5. attach к существующей tmux session;
6. восстановить terminal tabs;
7. восстановить открытые файлы;
8. вернуть пользователя в последнюю безопасную точку.

## Reconnect state machine

DISCONNECTED -> NETWORK_WAIT -> TAILSCALE_READY -> SSH_CONNECTING -> HOST_VERIFIED -> TMUX_ATTACHING -> READY.

При временном сбое используется bounded exponential backoff. При host-key mismatch, auth failure или revoked trust автоматическая петля прекращается и требуется явное действие пользователя.

## Tab identity

Терминальная вкладка связана не только с визуальным индексом, а с устойчивым remote id. Перестановка вкладок на телефоне не создаёт новые процессы.

## Crash recovery

После падения Android процесса приложение не пытается повторно выполнять последнюю команду. Оно только восстанавливает поток вывода существующей PTY/tmux session.

## Multiple workspaces

Поддерживаются отдельные рабочие пространства, например:

- ATLAS_EXECUTION_NODE;
- Mobile backend;
- Logs/diagnostics;
- будущий физический PC.

Переключение workspace не закрывает удалённые tmux-сессии по умолчанию.

## State schema

Схема состояния версионируется. Migration обязательна между версиями приложения. Повреждённое локальное состояние не должно блокировать запуск: fallback = новый пустой workspace без удаления удалённых сессий.

## Gate

Acceptance включает: kill app, rotate/recreate activity, Wi-Fi->4G, VPN/Tailscale reconnect, reboot телефона, reconnect к тому же tmux и восстановление UI без повторного запуска команд.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
