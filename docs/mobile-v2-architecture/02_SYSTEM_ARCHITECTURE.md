# ATLAS Mobile 2 — Этап 2. Системная архитектура

Статус: **ЗАФИКСИРОВАНО**

## 1. Архитектурный принцип

ATLAS Mobile 2 разделяется на два независимых контура:

1. **Control Plane** — управление ATLAS, доверие устройств, состояние машин, jobs, health, capabilities и API.
2. **Terminal Data Plane** — интерактивный низколатентный терминал и передача файлов.

Терминал не должен зависеть от WebView и не должен проходить через лишний HTTP-прокси, если прямой защищённый путь до машины доступен.

## 2. Целевая схема

```text
ANDROID / ATLAS MOBILE 2
│
├── UI / Compose
│   ├── Терминал
│   ├── Код
│   ├── Файлы
│   ├── ATLAS
│   ├── Машины
│   └── Настройки
│
├── Application Core
│   ├── Session Orchestrator
│   ├── Connection State Machine
│   ├── Device Identity
│   ├── Machine Repository
│   ├── Secure Storage
│   └── Localization
│
├── CONTROL PLANE
│   └── HTTPS/WSS → ATLAS Mobile Gateway RC2+
│                 ├── /version
│                 ├── health
│                 ├── device trust
│                 ├── machines
│                 ├── jobs
│                 └── capabilities
│
└── TERMINAL DATA PLANE
    └── SSH over Tailscale → NucBox / future PC
                          └── PTY → tmux → shell
```

## 3. Почему терминал использует прямой SSH как основной путь

Для terminal-first приложения основной путь должен быть максимально коротким:

```text
Android → Tailscale mesh → SSH → NucBox → PTY/tmux
```

Преимущества:

- меньше компонентов в интерактивном пути;
- ниже задержка;
- используется зрелый SSH protocol;
- штатный PTY/window-resize;
- зрелая аутентификация и host-key verification;
- не требуется писать собственный terminal protocol поверх WebSocket;
- терминал способен работать даже если UI Gateway временно недоступен, при условии сохранённого доверенного SSH-профиля.

Gateway остаётся центральной точкой identity/control, но не становится обязательным relay для каждого нажатия клавиши.

## 4. Fallback транспорт

Архитектура предусматривает интерфейс `TerminalTransport`, чтобы в будущем можно было добавить:

```text
Gateway PTY / WSS
```

как fallback для сред, где прямой SSH недоступен.

Первичная реализация не должна смешивать оба протокола в UI. Выбор транспорта производится Session Orchestrator по профилю машины.

Интерфейс уровня домена:

```text
TerminalTransport
├── connect(profile)
├── authenticate(identity)
├── openPty(term, rows, cols)
├── send(bytes)
├── resize(rows, cols)
├── close()
└── events: StateFlow<TransportEvent>
```

## 5. Tailscale

На первом production-ready этапе используется установленный на Android официальный Tailscale-клиент и системная сеть Android.

ATLAS Mobile:

- не реализует VPN самостоятельно;
- не хранит Tailscale auth keys;
- проверяет достижимость MagicDNS hostname;
- показывает отдельное состояние `TAILSCALE_UNAVAILABLE`, если tailnet недоступен;
- не переключается молча на публичный Интернет/неизвестный hostname.

Основные логические endpoints:

- Gateway: `tinvest-robot.tailf87948.ts.net` по HTTPS;
- NucBox: `atlas-omega-nucbox.tailf87948.ts.net` по SSH;
- будущий PC получает собственный machine profile и проходит explicit trust.

Hostnames должны храниться в профиле/конфигурации, а не размазываться по UI-коду.

## 6. Android-внутренняя модульность

На следующей реализации используется **один Android application module**, но с жёсткими package boundaries. Это уменьшает Gradle-сложность на ранней стадии, сохраняя возможность позже физически разделить Gradle modules.

```text
omega.atlas.mobile.v2
│
├── app/
│   ├── AtlasApplication
│   ├── navigation
│   └── lifecycle
│
├── core/
│   ├── model
│   ├── network
│   ├── security
│   ├── storage
│   ├── localization
│   └── diagnostics
│
├── terminal/
│   ├── emulator
│   ├── transport
│   ├── session
│   ├── tmux
│   ├── input
│   └── ui
│
├── connections/
│   ├── profiles
│   ├── enrollment
│   └── ui
│
├── files/
│   ├── remote
│   ├── cache
│   └── ui
│
├── code/
│   ├── editor
│   ├── bridge
│   └── ui
│
├── atlas/
│   ├── gateway
│   ├── machines
│   ├── jobs
│   └── ui
│
└── settings/
    └── ui
```

## 7. UI architecture

Используется однонаправленный поток состояния:

```text
User Action
   ↓
ViewModel / Controller
   ↓
Domain use-case
   ↓
Repository / Session Service
   ↓
StateFlow
   ↓
Compose UI
```

UI не открывает сокеты напрямую и не хранит network connection в Activity.

## 8. Владение терминальной сессией

Критическое решение:

**SSH-сессиями владеет foreground session service, а не Activity/Composable.**

```text
TerminalSessionService
├── Session A → SSH → tmux A
├── Session B → SSH → tmux B
└── Session C → SSH → tmux C
```

Compose UI подписывается на состояние и terminal buffers. Это позволяет переживать:

- rotation;
- navigation между экранами;
- временное сворачивание;
- пересоздание Activity;
- смену Wi-Fi/4G с reconnect.

При полном убийстве Android-процесса удалённый `tmux` остаётся жив и восстанавливается после нового запуска приложения.

## 9. Background policy

Пока есть активная terminal session:

- работает Android Foreground Service;
- отображается ненавязчивое уведомление `ATLAS: N активных сессий`;
- постоянный wakelock не держится;
- приложение использует network callbacks;
- reconnect выполняется с ограниченным exponential backoff;
- после длительной недоступности сети session переходит в `SUSPENDED`, не спамит соединениями.

Когда активных terminal sessions нет, foreground service останавливается.

## 10. Source of truth

Разделение источников истины:

- terminal runtime state → `TerminalSessionService`;
- remote process continuity → `tmux` на целевой машине;
- device identity/credentials → secure storage;
- machine profiles → локальный repository + Gateway reconciliation;
- ATLAS machine/job state → Gateway;
- UI state → ViewModel/StateFlow.

## 11. Compatibility boundary

Новая архитектура не требует удаления текущего RC2 и не меняет его контракт автоматически.

Новые backend endpoints добавляются только как additive API version:

```text
/api/v2/mobile/...
```

Старые `/version` и RC2 endpoints продолжают работать.

## 12. Архитектурное решение

Основной production путь терминала:

```text
Direct SSH over Tailscale + server-side tmux
```

Control plane:

```text
HTTPS/WSS via ATLAS Mobile Gateway
```

Это решение считается базовым до отдельного ADR, который его изменит.

**ARCHITECTURE_STAGE_2 = COMPLETE**
