# Этап 31 — Additive backend contracts для V2

Статус: ARCHITECTURE ONLY. Backend код не меняется. APK не собирается.

## Цель

Определить минимальный набор новых backend-возможностей для V2, сохранив существующий RC2 API совместимым.

## Принцип

Никаких breaking changes в существующих RC2 endpoint/semantics. Новые возможности добавляются отдельными versioned routes/events.

## Control-plane contracts

### Device enrollment

Контракт должен поддерживать состояния:

UNREGISTERED -> PENDING_TRUST -> TRUSTED -> REVOKED.

Клиент получает только собственный device id/status/capabilities. Trust elevation требует явного server-side approval.

### Machines

Read-only machine summary:
- machine id;
- display name;
- online/offline;
- capabilities;
- last heartbeat;
- health layers.

### Workspaces

Минимальная remote metadata:
- workspace id;
- machine id;
- project root;
- tmux namespace/session identity;
- optional presence/lease metadata;
- protocol/schema version.

### Jobs

Существующий job model сохраняется. V2 требует только ясного read/status/history contract и безопасного submit contract для разрешённых capabilities.

## Terminal plane

Предпочтительный V2 data-plane остаётся direct SSH over Tailscale. Gateway не обязан проксировать полный PTY-трафик.

Backend может предоставлять только metadata/session coordination:
- recommended machine endpoint;
- workspace/tmux identity;
- presence;
- policy/capability status.

Это уменьшает latency и нагрузку Gateway.

## Health

Нужен layered health contract, где отдельными полями представлены:
- gateway;
- vm agent;
- nucbox agent;
- machine heartbeat;
- trust;
- optional workspace/session availability.

Один boolean ONLINE не используется как единственная истина.

## Versioning

Каждый response содержит api/schema version. Неизвестные optional fields игнорируются клиентом; изменение required semantics требует новой версии маршрута/контракта.

## Error contract

Backend ошибки имеют stable machine-readable code + русифицируемый client mapping. Server message хранится как technical detail, а не как готовая пользовательская локализация.

## Capability invariants

Новые mobile capabilities не включают live trading authority. Терминал/код/файлы и research jobs остаются отделены от торгового исполнения.

## Compatibility tests

Перед любым backend change выполняются:
- старый RC2 client compatibility smoke;
- V2 contract tests;
- additive schema test;
- authorization/capability test;
- no-live-authority invariant.

## Gate

Backend implementation не начинается до отдельной команды START IMPLEMENTATION. Этот документ является контрактом, а не разрешением на деплой.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
