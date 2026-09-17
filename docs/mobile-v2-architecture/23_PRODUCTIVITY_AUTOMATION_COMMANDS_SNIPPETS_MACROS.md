# Этап 23 — Productivity automation: command palette, snippets, macros

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Сократить количество касаний и ручного набора на телефоне без превращения автоматизации в скрытое выполнение команд.

## Command palette

Глобальная палитра действий вызывается одной кнопкой/жестом и умеет искать по русским названиям и техническим alias.

Примеры действий:

- открыть терминал;
- перейти к файлу;
- открыть Git diff;
- запустить Fast Gate;
- прикрепиться к tmux;
- показать ошибки;
- открыть последний traceback;
- спросить ATLAS AI;
- перейти к машине/workspace.

Палитра показывает, является действие read-only, write или destructive.

## Snippets

Snippets — параметризованные текстовые шаблоны для shell/code, например типовые pytest/systemctl/git/python команды.

Правила:

- snippet вставляет текст по умолчанию, но не выполняет его;
- placeholder редактируются перед отправкой;
- секреты не сохраняются в snippet;
- пользовательские snippets синхронизируются только как несекретный текст.

## Macros

Macro — последовательность явных действий приложения, а не произвольный скрытый script engine.

Пример безопасного macro:

1. открыть workspace;
2. показать git status;
3. открыть тестовый терминал;
4. вставить команду тестов;
5. ждать явного Run пользователя, если macro содержит write/execute step.

Автоисполнение разрешено только для заранее классифицированных read-only действий. Shell execution требует подтверждения или явно настроенного trusted local macro profile.

## Recent and favorites

Приложение ведёт локальную историю быстрых действий без содержания секретов:

- последние каталоги;
- последние файлы;
- последние безопасные команды как text history;
- избранные snippets;
- избранные workspaces.

## Context actions

Контекст терминала и редактора предлагает релевантные действия:

- traceback -> открыть `path:line`;
- test failure -> открыть test + implementation;
- git conflict -> открыть conflict editor;
- permission error -> показать диагностику, не предлагать автоматический sudo;
- command not found -> предложить поиск/проверку PATH.

## Voice/clipboard optionality

Архитектура допускает голосовой ввод текста и обработку clipboard, но они никогда не отправляются автоматически в shell. Любой внешний ввод проходит preview.

## Automation safety classes

A0 — view/navigation, можно автоматически.
A1 — prepare text, можно автоматически без Enter.
A2 — execute non-destructive command, требуется явный Run или trusted profile.
A3 — write/change state, всегда подтверждение.
A4 — destructive/security-sensitive, отдельное усиленное подтверждение; часть действий может быть вообще недоступна из мобильного UI.

## Metrics

Измеряем не только время сборки приложения, но и пользовательскую эффективность:

- taps to open terminal;
- taps to run test;
- taps to open traceback source;
- taps to commit reviewed change;
- median reconnect-to-ready time;
- characters saved by snippets/keyboard.

## Gate

Ни один macro/snippet/command palette action не должен обходить существующую trust/capability/security model.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
