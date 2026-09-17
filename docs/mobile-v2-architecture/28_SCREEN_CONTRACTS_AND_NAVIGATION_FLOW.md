# Этап 28 — Screen contracts и navigation flow

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Зафиксировать экранную модель до реализации Compose, чтобы не повторить alpha1, где форма подключения заняла главный рабочий экран.

## Главные экраны

### 1. Terminal Workspace

Стартовый экран приложения.

Содержит:
- верхнюю строку workspace/machine/status;
- terminal tabs;
- полноэкранный terminal viewport;
- compact programmer keyboard;
- быстрые переходы Код/Файлы/Git/ATLAS;
- reconnect indicator без блокирующего modal.

Не содержит host/user/password fields.

### 2. Connections

Отдельный экран управления connection profiles:
- машины;
- trust state;
- host/user/port;
- credential enrollment;
- host key fingerprint;
- test connection;
- revoke/remove profile.

### 3. Code

- file tabs;
- editor;
- current symbol/path/line;
- diagnostics;
- run/insert to terminal;
- AI actions;
- save/conflict state.

### 4. Files

- workspace root;
- tree/list;
- search;
- open/rename/new/delete with confirmation;
- upload/download optional;
- file metadata.

### 5. Git

- status;
- staged/unstaged;
- diff;
- branches;
- commits;
- conflicts;
- test status tied to worktree fingerprint.

### 6. ATLAS

Native control-plane screen:
- machines;
- jobs;
- health;
- capabilities;
- trust requests;
- safe diagnostics.

### 7. Settings

- language;
- terminal font/colors;
- keyboard profiles;
- scrollback;
- reconnect policy bounds;
- diagnostics export;
- app/about/version.

## Navigation rule

Из Terminal Workspace до Code/Files/Git/ATLAS максимум 1 действие.

Возврат назад не должен терять terminal focus/session.

## Bottom navigation

На маленьком экране постоянная bottom navigation допускается только если не уменьшает terminal viewport критично. Предпочтительно compact rail/popup/command palette в landscape и скрываемая bottom bar в portrait.

## Fullscreen terminal

Отдельный режим скрывает все chrome элементы кроме минимального session/status affordance и programmer keyboard. Выход жестом/кнопкой Back не закрывает удалённую сессию.

## Error presentation

Ошибки terminal connection отображаются inline status panel с действиями Повторить/Диагностика/Подключения. Не закрывают весь terminal, если scrollback всё ещё полезен.

## Empty states

Если профиль ещё не создан, стартовый terminal screen показывает короткое onboarding action «Добавить подключение», а не длинную форму.

## Russian UX

Все labels/user errors/help на русском. Технические строки, hostnames, paths, shell output не переводятся.

## Accessibility

Минимальные touch targets, масштабируемый шрифт, screen-reader labels для управляющих кнопок, contrast checks.

## Gate

Перед implementation каждый экран должен иметь preview/fake state: loading, ready, error, disconnected, empty.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
