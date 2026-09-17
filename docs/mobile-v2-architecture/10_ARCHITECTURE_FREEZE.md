# ATLAS Mobile 2 — Этап 10. Architecture Freeze

Статус: **ARCHITECTURE READY / IMPLEMENTATION NOT STARTED**

Дата фиксации: 2026-09-17

## 1. Зафиксированные этапы

1. `01_REQUIREMENTS_AND_INVARIANTS.md` — цели, terminal-first, русификация, safety invariants.
2. `02_SYSTEM_ARCHITECTURE.md` — Control Plane / Terminal Data Plane, lifecycle и service ownership.
3. `03_TERMINAL_FIRST_UX_AND_SESSIONS.md` — полноэкранный терминал, tabs, tmux, reconnect, keyboard/input.
4. `04_IDENTITY_SECURITY_AND_ENROLLMENT.md` — device identity, trust, credential vault, host-key pinning.
5. `05_CODE_FILES_AND_TERMINAL_BRIDGE.md` — SFTP/files/editor/terminal bridge/Git read layer.
6. `06_RUSSIAN_UX_NAVIGATION.md` — полная русификация, navigation, statuses, onboarding.
7. `07_CONTROL_PLANE_AND_BACKEND_COMPATIBILITY.md` — additive backend evolution и RC2 compatibility.
8. `08_TESTING_AND_ACCEPTANCE.md` — CI, integration, emulator, real-device, stress, acceptance.
9. `09_IMPLEMENTATION_BLUEPRINT.md` — будущая реализация по фазам A–J.

## 2. Ключевые архитектурные решения

### ADR-A: Terminal First

Терминал — главный рабочий экран приложения. После onboarding пользователь не видит большую SSH-форму при каждом запуске.

### ADR-B: Direct SSH over Tailscale

Основной terminal data path:

```text
Android → Tailscale → SSH → PTY → tmux → shell
```

### ADR-C: Gateway as Control Plane

Gateway отвечает за version/health/machines/jobs/device identity/capabilities, но не обязан relay'ить каждый terminal byte.

### ADR-D: tmux continuity

Remote `tmux` является источником непрерывности terminal workload при потере Android connection/process.

### ADR-E: Session Service owns connections

SSH sessions принадлежат Foreground Service/Session Manager, не Activity/Composable.

### ADR-F: Secure per-device credentials

Каждая установка имеет отдельный device credential; секрет не вшивается в APK и защищён Android Keystore-backed storage.

### ADR-G: Explicit trust

Новые устройства и новые/изменённые host keys требуют явного trust. Silent trust запрещён.

### ADR-H: Russian-first UI

Русский — основной язык UI. Terminal output остаётся оригинальным.

### ADR-I: Native development workflow

Files/Code/Terminal интегрируются native; WebView не используется как terminal renderer.

### ADR-J: Additive backend evolution

RC2 не переписывается ради Android V2. Новые backend capabilities добавляются совместимо и проходят rollback/E2E gates.

## 3. Target daily workflow

После первичной настройки:

```text
Открыть ATLAS Mobile 2
        ↓
восстановить последнюю workspace/session
        ↓
проверить Tailscale/SSH
        ↓
attach к tmux
        ↓
ТЕРМИНАЛ ГОТОВ
        ↓
писать/запускать код
```

Цель: никаких повторных host/user/key форм в обычной ежедневной работе.

## 4. Основные экраны

```text
Терминал  ← главный
Код
Файлы
ATLAS
```

Дополнительные:

```text
Машины
Подключения
Задания
Мониторинг
Настройки
О приложении
```

## 5. Safety freeze

Неизменяемые требования:

```text
LIVE_TRADING_ENABLED = NO
live_trading_authority = ABSENT
RESEARCH_ONLY = YES
```

Мобильный клиент не получает автоматические торговые полномочия.

## 6. Release gate

Архитектурная готовность не равна готовности APK.

Будущий артефакт проходит:

```text
SOURCE_VALID
BUILD_VALID
STATIC_VALID
UNIT_VALID
INTEGRATION_VALID
EMULATOR_VALID
REAL_DEVICE_VALID
END_TO_END_VALID
```

До real-device/E2E нельзя объявлять новую версию `READY_FOR_DAILY_USE`.

## 7. Current prototype status

Существующая `0.2.0-alpha1` остаётся только техническим прототипом, доказавшим работоспособность Compose/terminal/SSH build stack и установку APK. Её крупная SSH-форма и Activity-owned UX не являются целевой архитектурой.

## 8. Implementation lock

На момент freeze:

```text
ARCHITECTURE = READY
IMPLEMENTATION = WAITING_FOR_USER_COMMAND
NEW_APK_BUILD = FORBIDDEN_UNTIL_USER_COMMAND
BACKEND_CHANGES = NOT_STARTED
DEPLOYMENT = NOT_STARTED
```

## 9. Следующая разрешённая операция

Только после явной команды пользователя начинается Phase A из `09_IMPLEMENTATION_BLUEPRINT.md`.

Рекомендуемая будущая версия после начала реализации:

```text
ATLAS Mobile 2 — Terminal First
0.2.x development line
```

Конкретный versionName определяется в начале реализации, а не в архитектурном freeze.

**ARCHITECTURE_STAGE_10 = COMPLETE**
**ATLAS_MOBILE_2_ARCHITECTURE = READY**
