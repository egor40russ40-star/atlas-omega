# ATLAS Mobile 2 — Этап 7. Control Plane и совместимость с backend

Статус: **ЗАФИКСИРОВАНО**

## 1. Правило совместимости

Существующий ATLAS Mobile backend RC2 считается рабочей базой и не переписывается ради нового Android-клиента.

Новая мобильная архитектура использует принцип:

```text
additive evolution, not replacement
```

То есть новые возможности добавляются отдельными контрактами, а существующие `/version` и текущие RC2 endpoints продолжают работать.

## 2. Version contract

При старте клиент проверяет `/version` и получает минимум:

```text
product
version
api_version
mode
identity_mode
live_trading_authority
```

Клиент обязан проверять safety invariant:

```text
live_trading_authority == ABSENT
```

Несовместимая версия API не должна приводить к молчаливому использованию неизвестных endpoints.

## 3. API namespaces

Старый API остаётся как есть.

Новые mobile-native контракты проектируются под версионированным namespace:

```text
/api/v2/mobile/...
```

или эквивалентным versioned router, если backend использует другую принятую схему.

## 4. Control Plane domains

Новый Android client ожидает логические домены, а не обязательно конкретную реализацию endpoint на первом этапе:

```text
VersionService
DeviceService
MachineService
JobService
HealthService
CapabilityService
AuditService
```

Android слой зависит от интерфейсов repository, а endpoint mapping изолируется в gateway adapter.

## 5. Device service

Логический контракт:

```text
registerDevice(publicIdentity)
getDeviceState(deviceId)
getCapabilities(deviceId)
revokeSession()
```

Операция, реально выдающая trust устройству, не должна быть доступна самому неподтверждённому телефону как self-approval.

## 6. Machine registry

Machine profile из Gateway может содержать:

```text
machine_id
display_name
role
reachable_hostname
terminal_transport
ssh_port
host_key_fingerprint
workspace_hints
capabilities
health_state
last_seen
```

Private credentials не входят в machine profile.

## 7. Health model

Состояния не сводятся к одному boolean.

Пример:

```text
GatewayHealth
MachineHealth
AgentHealth
TerminalReachability
```

Android отображает отдельные слои и способен различить:

```text
Gateway доступен, NucBox недоступен
Gateway недоступен, SSH к NucBox доступен
SSH доступен, agent unhealthy
```

## 8. Job model

Для development jobs клиент использует Control Plane, а не исполняет их через скрытый terminal command.

Job contract:

```text
Job
├── id
├── action
├── machine_id
├── state
├── created_at
├── started_at
├── finished_at
├── exit_code
├── sanitized_output
└── failure_reason
```

Состояния:

```text
QUEUED
CLAIMED
RUNNING
SUCCEEDED
FAILED
CANCELLED
EXPIRED
```

## 9. Terminal не зависит от Job API

Terminal session и control jobs разделены.

Причина:

- terminal требует интерактивный byte stream;
- jobs требуют аудируемый конечный lifecycle;
- смешивание создаёт ложные таймауты и трудный recovery.

## 10. Native ATLAS screen

Долгосрочно Android получает native данные:

- состояние Gateway;
- машины;
- agent health;
- jobs;
- capabilities;
- version/safety;
- selected diagnostics.

Legacy WebView может оставаться временным compatibility adapter, но не является core architecture.

## 11. Caching

Разрешён небольшой локальный cache:

- machine list;
- display names;
- last health snapshot;
- recent jobs metadata.

UI всегда маркирует stale/offline данные.

Критические authorization/capability решения не принимаются только по кешу.

## 12. Retry policy

GET/read операции:

- допускают bounded retry;
- exponential backoff;
- cancellation при уходе экрана.

State-changing operations:

- используют idempotency key там, где backend поддерживает;
- не повторяются автоматически без уверенности в идемпотентности;
- UI показывает `Состояние операции неизвестно`, если ответ потерян после отправки.

## 13. Error envelope

Новый API должен стремиться к машинно читаемой ошибке:

```text
code
message_ru / user_message_key
technical_detail
request_id
retryable
```

Клиент не зависит от локализованного серверного текста как от программного кода ошибки.

## 14. Audit correlation

Для значимых control действий Android создаёт `request_id/correlation_id`, чтобы можно было связать:

```text
mobile event
→ gateway request
→ agent job
→ evidence/log
```

Terminal keystrokes по умолчанию не превращаются в централизованный command audit.

## 15. Backward compatibility gate

Перед добавлением любого нового backend endpoint обязательны:

1. backup/rollback;
2. существующий `/version` PASS;
3. текущий RC2 selfcheck PASS;
4. новый endpoint test;
5. старый E2E не сломан;
6. `live_trading_authority = ABSENT`.

## 16. Failure isolation

Отказ нового `/api/v2/mobile` не должен останавливать старый RC2 service.

Желательно:

- отдельный router/module;
- отдельные schema migrations с rollback;
- feature flags;
- health endpoint на новый модуль.

## 17. PC extension

Будущий физический PC подключается через тот же Machine Registry contract. Android не содержит отдельного hardcoded workflow для каждой новой машины.

```text
Machine Profile → transport/capabilities/workspaces
```

## 18. Safety

Новый Control Plane не расширяет торговые права мобильного устройства.

```text
LIVE_TRADING_ENABLED = NO
live_trading_authority = ABSENT
RESEARCH_ONLY = YES
```

**ARCHITECTURE_STAGE_7 = COMPLETE**
