# Этап 29 — Миграция с alpha1 и rollback

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Перейти от установленного alpha1 к новой архитектуре без потери рабочего доступа и с возможностью быстрого отката.

## Package strategy

До real-device acceptance новая реализация сохраняет отдельный applicationId/variant, чтобы alpha1 мог оставаться установленным параллельно.

После подтверждения стабильности принимается отдельное решение: продолжать side-by-side package или перевести release channel на единый package с migration.

## Что не переносим автоматически

- raw password;
- imported private key bytes;
- временные SSH session objects;
- непроверенные host fingerprints.

Credential migration должна либо повторно enroll устройство, либо использовать безопасный Keystore-compatible migration, если он доказуемо возможен.

## Что можно переносить

- host/display name;
- username/port как несекретную metadata;
- gateway URL при прохождении HTTPS validation;
- UI preferences;
- keyboard preferences после schema validation.

## First-run migration

Новая версия определяет наличие alpha1 metadata и предлагает:

1. импортировать безопасные настройки;
2. повторно подтвердить host identity;
3. создать/привязать credential;
4. проверить Gateway;
5. проверить SSH;
6. создать первый workspace;
7. выполнить read-only self-test.

Пока self-test не завершён, alpha1 не удаляется автоматически.

## Rollback

Rollback = установка/запуск предыдущего клиента без изменения backend RC2 и без удаления удалённых tmux sessions.

Remote state должен оставаться совместимым настолько, чтобы клиентский rollback не требовал отката серверных данных.

## Migration evidence

Фиксируется локальный/CI report:
- source version;
- target version;
- migrated fields;
- skipped sensitive fields;
- connection test result;
- workspace creation result.

Без секретов.

## Failure behavior

Если migration ломается:
- новая версия остаётся в safe onboarding;
- alpha1 не модифицируется;
- backend не откатывается;
- remote sessions не закрываются.

## Gate

До APK_CANDIDATE должны быть тесты clean install, side-by-side install, migration from alpha1 metadata и rollback to previous client.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
