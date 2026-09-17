# Этап 20 — Интеграция ATLAS AI в coding workflow

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

ATLAS AI должен быть встроенным помощником разработчика, а не отдельным чат-экраном, который не знает текущий файл, terminal output и workspace.

## Контекст

Помощник может получать только явно разрешённый контекст:

- текущий файл/выделение;
- выбранный набор файлов;
- Git diff;
- terminal output;
- diagnostics/test failures;
- metadata workspace без секретов.

Секреты, private keys, токены и credential storage автоматически исключаются.

## Основные действия

Из редактора:

- объяснить выделенный код;
- найти ошибку;
- предложить patch;
- написать тест;
- рефакторинг;
- документировать;
- объяснить traceback.

Из терминала:

- объяснить последние N строк;
- предложить следующую диагностическую команду;
- открыть упомянутый `path:line`;
- сформировать команду в preview;
- создать patch proposal.

## Никаких скрытых изменений

AI не пишет напрямую в рабочие файлы без preview.

Flow:

AI proposal -> diff preview -> user approve -> atomic apply -> targeted tests -> result.

Для shell-команд:

AI command proposal -> terminal preview -> explicit Run.

## Intelligence Router

Запросы маршрутизируются по сложности:

- status/объяснение простой ошибки -> минимальный reasoning;
- обычный code fix -> medium;
- multi-file refactor/architecture -> high;
- критическая конфликтующая диагностика -> maximum available.

Эскалация автоматическая при провале теста, неполном контексте или затрагивании нескольких подсистем.

## Cost/time optimization

Перед AI-вызовом локальный анализатор собирает минимальный релевантный контекст, чтобы не отправлять весь проект. Используются file index, symbol index, Git diff и error locations.

## Patch representation

AI-изменения представлены структурированным patch set с:

- files touched;
- hunks;
- rationale;
- expected tests;
- risk class;
- rollback reference.

## Safety

AI не получает полномочий live trading, credential rotation или trust elevation. Такие действия исключены на уровне capabilities.

## Gate

Acceptance: любой AI-generated change должен быть просматриваемым, обратимым и проверенным соответствующим test gate перед фиксацией.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
