# Этап 30 — Release, signing и update architecture

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Сделать выпуск APK воспроизводимым, проверяемым и отделённым от обычной разработки.

## Build channels

Определяются каналы:

- dev/debug — быстрые локальные/CI проверки;
- alpha — real-device тесты;
- beta — стабилизация;
- release — только после полного acceptance.

## Signing

Release signing key не хранится в репозитории и не вшивается в исходники.

CI получает signing material только через защищённый secret mechanism во время release job. Debug/alpha могут иметь отдельную тестовую подпись.

## Reproducibility

Для каждого candidate фиксируются:

- commit SHA;
- dependency lock/versions;
- Gradle/Java/SDK versions;
- build type;
- APK SHA-256;
- signing certificate fingerprint;
- test/acceptance report ids.

## Candidate promotion

Новый APK не пересобирается заново между beta и release без необходимости. Предпочтительно продвигать уже проверенный immutable artifact, если подпись/канал позволяет.

## Update checks

Приложение может проверять наличие новой версии через control-plane metadata, но:

- не скачивает/устанавливает APK скрытно;
- показывает version/changelog/hash;
- пользователь явно подтверждает обновление;
- production/release update source должен быть доверенным.

## Compatibility matrix

Каждый release содержит min/max supported backend API version и terminal/session protocol version.

Если backend несовместим, приложение показывает понятное сообщение и не пытается работать в частично неизвестном режиме.

## Rollback artifact retention

Хранятся последние проверенные release/beta artifacts и checksums. Старые артефакты не удаляются автоматически до истечения retention policy.

## Supply-chain checks

Перед release:

- dependency verification/lock;
- known dependency audit;
- manifest permissions diff;
- exported components audit;
- network security config audit;
- APK signature verification;
- artifact SHA verification.

## Permissions discipline

Добавление нового Android permission автоматически повышает risk class изменения и требует Full Gate + review причины.

## Changelog

Changelog генерируется из структурированных change metadata, но перед release проверяется вручную/архитектурным gate. Пользовательские изменения описываются по-русски.

## Gate

RELEASE_ACCEPTED возможен только при наличии successful Full Gate, real-device acceptance, checksum, signature verification и совместимости backend.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
