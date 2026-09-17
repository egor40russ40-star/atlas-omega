# ATLAS Mobile 2 — Этап 4. Identity и Security Architecture

Статус: **ЗАФИКСИРОВАНО**

## 1. Базовый принцип

Каждая установка ATLAS Mobile 2 рассматривается как отдельное устройство со своей идентичностью. Доверие новому устройству никогда не выдаётся автоматически.

Состояния устройства:

```text
UNREGISTERED → REGISTERING → PENDING_TRUST → TRUSTED → READY
```

Отдельные состояния:

```text
REVOKED
EXPIRED
ROTATION_REQUIRED
```

## 2. Ключи устройства

Для каждой установки создаётся отдельная пара ключей. Приватная часть не вшивается в APK, не хранится в Git/CI и не передаётся в Gateway.

Приватный материал хранится только в private storage приложения в зашифрованном виде. Ключ шифрования защищается Android Keystore. Публичная часть используется при регистрации устройства.

Доменный контракт:

```text
CredentialVault
├── createDeviceCredential()
├── importCredential()      # только advanced/recovery
├── loadForSession()
├── rotate()
└── revokeLocal()
```

UI не должен держать raw private key в обычном persistent state.

## 3. Enrollment

Логика регистрации:

```text
Телефон создаёт device identity
        ↓
передаёт public identity в Control Plane
        ↓
PENDING_TRUST
        ↓
явное подтверждение доверия
        ↓
получает только разрешённые machine profiles/capabilities
```

До явного подтверждения устройство не получает доступ к developer sessions.

## 4. SSH host trust

Предпочтительно получать ожидаемый host-key fingerprint из доверенного machine registry. Если это недоступно, разрешён TOFU с явным подтверждением fingerprint пользователем.

После первичного подтверждения fingerprint фиксируется. Любое изменение переводит соединение в:

```text
HOST_KEY_CHANGED
```

и блокирует автоматическое подключение до отдельного подтверждения.

Режим `accept all host keys` запрещён.

## 5. Gateway security

- только HTTPS;
- cleartext traffic запрещён Network Security Config;
- certificate/hostname errors не обходятся;
- API ошибки TLS не преобразуются в «продолжить всё равно»;
- endpoint выбирается из доверенного machine/control profile.

## 6. Password mode

SSH-пароль допускается только как временный recovery/advanced вариант.

- пароль не сохраняется;
- не попадает в persistent state;
- очищается после использования;
- основной режим — отдельный device credential.

## 7. Capability model

Мобильный клиент может иметь development/read capabilities, например:

```text
CAP_TERMINAL
CAP_FILES_READ
CAP_FILES_WRITE
CAP_DEV_JOBS
CAP_MACHINE_STATUS
CAP_ATLAS_CONTROL_READ
```

Мобильному устройству не выдаются автоматически:

```text
CAP_LIVE_TRADING
CAP_GRANT_TRUST
CAP_ROOT_AUTOMATION
```

Проверка capability выполняется серверной стороной для действий Control Plane, а не только скрытием кнопки в UI.

## 8. Logs и telemetry

Запрещено логировать:

- private keys;
- key passphrase;
- SSH password;
- authorization tokens;
- clipboard content;
- полный ввод terminal commands по умолчанию.

Разрешены sanitized diagnostics:

- device/session id;
- machine id;
- transport state;
- error class;
- latency;
- reconnect count;
- host fingerprint.

## 9. Clipboard и screenshots

Terminal clipboard читается только по явному действию пользователя. Чувствительные onboarding/credential экраны могут временно запрещать screen capture. Обычный terminal screen не блокирует screenshot, чтобы пользователь мог работать с кодом и делиться диагностикой.

## 10. Revocation

При отзыве устройства:

```text
Device state → REVOKED
Control Plane credential → disabled
Machine access credential → disabled
New sessions → blocked
```

Повторное подключение требует нового enrollment и явного trust.

## 11. Rotation

Ротация выполняется без потери доступа по схеме:

```text
new credential → register → approve → verify → retire old
```

Старый credential удаляется только после подтверждённого входа новым.

## 12. Safety invariants

Identity/enrollment не меняют торговый режим системы:

```text
LIVE_TRADING_ENABLED = NO
live_trading_authority = ABSENT
RESEARCH_ONLY = YES
```

**ARCHITECTURE_STAGE_4 = COMPLETE**
