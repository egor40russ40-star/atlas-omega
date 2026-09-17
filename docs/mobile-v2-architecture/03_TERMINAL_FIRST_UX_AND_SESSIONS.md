# ATLAS Mobile 2 — Этап 3. Terminal-First UX и модель сессий

Статус: **ЗАФИКСИРОВАНО**

## 1. Главный экран

После завершённого onboarding приложение открывается не на форме подключения, а на последней рабочей terminal workspace.

Целевой вид телефона:

```text
┌────────────────────────────────┐
│ NucBox ● Подключено     [1] [+]│
├────────────────────────────────┤
│                                │
│                                │
│       ПОЛНОЭКРАННЫЙ PTY        │
│                                │
│ $ ~/ATLAS_EXECUTION_NODE       │
│                                │
│                                │
├────────────────────────────────┤
│ ESC TAB CTRL ALT  ↑ ↓ ← →      │
│ |  \\  ~  _  -  { }  [ ]       │
├────────────────────────────────┤
│ Терминал  Код  Файлы  ATLAS    │
└────────────────────────────────┘
```

Форма host/user/key не занимает постоянное место на terminal screen.

## 2. Профили подключения

Профили находятся в отдельном разделе:

```text
Подключения
├── NucBox
├── VM
└── Future PC
```

Поля профиля:

- display name;
- machine id;
- MagicDNS hostname;
- port;
- SSH username;
- transport type;
- host-key fingerprint;
- credential reference;
- default working directory;
- default tmux behavior;
- connection timeout;
- reconnect policy.

Пароль и приватный ключ не являются полями обычного profile storage; профиль хранит только ссылку на Secure Credential Store.

## 3. Терминальные вкладки

Каждая вкладка — самостоятельная `TerminalSession`:

```text
TerminalSession
├── id: UUID
├── machineProfileId
├── displayName
├── state
├── transport
├── terminalEmulator
├── tmuxSessionName
├── cwdHint
├── rows/cols
├── fontSize
└── timestamps
```

Функции вкладок:

- `+` новая сессия;
- переименование;
- duplicate session profile;
- reorder drag-and-drop;
- закрытие с подтверждением только если нет server-side persistence;
- цвет/иконка машины;
- индикатор `CONNECTED / RECONNECTING / SUSPENDED / FAILED`;
- счётчик activity для фоновой вкладки.

## 4. tmux как слой непрерывности

По умолчанию при новом terminal tab выполняется управляемая команда вида:

```text
tmux new-session -A -s <safe-session-name>
```

Имя генерируется приложением из device/session UUID и не содержит shell-инъекций.

Пример логического имени:

```text
atlas-mob-a13f-terminal-01
```

Пользователь может выбрать:

- `Автоматическая tmux-сессия` — default;
- `Обычный shell без tmux` — advanced;
- `Подключиться к существующей tmux`;
- `Выбрать tmux session`.

Приложение не подменяет tmux protocol: оно открывает обычный PTY и выполняет безопасно сформированную команду.

## 5. State machine терминала

```text
IDLE
 ↓ connect
RESOLVING_NETWORK
 ↓
CONNECTING
 ↓
VERIFYING_HOST
 ↓
AUTHENTICATING
 ↓
OPENING_PTY
 ↓
ATTACHING_TMUX
 ↓
READY
```

Ошибочные/переходные состояния:

```text
RECONNECTING
NETWORK_UNAVAILABLE
AUTH_REQUIRED
HOST_KEY_CHANGED
SUSPENDED
FAILED
CLOSING
CLOSED
```

UI никогда не показывает общее `ONLINE`, если не достигнут `READY`.

## 6. Reconnect policy

При потере сети:

1. terminal emulator остаётся на экране с последним buffer;
2. input блокируется или помещается в короткую локальную очередь только для безопасного периода;
3. session state → `RECONNECTING`;
4. reconnect backoff: 1s, 2s, 4s, 8s, затем ограниченный интервал;
5. после восстановления SSH приложение повторно attach к той же tmux-сессии;
6. никакая команда не отправляется повторно автоматически, если неизвестно, была ли она доставлена до разрыва.

Это предотвращает дублирование потенциально опасных команд.

## 7. Input pipeline

Ввод разделяется на два типа:

### Raw terminal input

Используется для:

- CTRL sequences;
- ESC;
- arrows;
- TAB;
- function/navigation keys;
- hardware keyboard key events.

Передаётся как корректные terminal byte sequences.

### IME text input

Используется для обычного текста и Unicode.

Требования:

- отключить autocorrect/prediction там, где Android позволяет;
- не заменять кавычки на smart quotes;
- не модифицировать пробелы и переносы;
- поддерживать кириллицу в shell там, где locale удалённой системы её поддерживает;
- paste всегда передаёт исходный clipboard text без автокоррекции.

## 8. Спецклавиатура

Панель состоит из двух горизонтальных рядов и может прокручиваться только при явной нехватке ширины. Базовый набор должен помещать критические клавиши без необходимости прокрутки.

### Ряд 1 — управление

```text
ESC  TAB  CTRL  ALT  ↑  ↓  ←  →
```

### Ряд 2 — код

```text
|  \\  ~  _  -  {  }  [  ]  (  )
```

Дополнительная панель по swipe/expand:

```text
HOME END PGUP PGDN
: ; = + ' " ` & * < >
CTRL+C CTRL+D CTRL+Z CTRL+L CTRL+R CTRL+A CTRL+E CTRL+W
```

## 9. Modifier keys

`CTRL`, `ALT`, `SHIFT` имеют три режима:

- tap → применить к следующей клавише;
- double tap → lock;
- long press → открыть быстрый список комбинаций.

Активный modifier визуально подсвечивается.

После применения one-shot modifier сбрасывается.

## 10. Жесты терминала

- pinch → terminal font size;
- вертикальный scroll → scrollback;
- long press → selection mode;
- tap по выделению → toolbar Copy;
- paste — только явным действием;
- double tap по слову → выделить слово;
- swipe по tab bar → следующая/предыдущая terminal session;
- системный back не закрывает активную session без предсказуемого поведения.

## 11. Scrollback

По умолчанию локально хранится ограниченный circular buffer, целевой порядок 20–50 тыс. строк на вкладку с адаптацией по памяти.

Требования:

- поиск по текущему buffer;
- переход вверх/вниз по совпадениям;
- кнопка `В конец` при просмотре истории;
- incoming output не сбрасывает позицию пользователя, если он читает scrollback;
- при возвращении в live tail появляется понятный индикатор.

## 12. Terminal resize

Источник размеров — фактическая область terminal canvas после учёта:

- status/navigation bars;
- bottom navigation;
- custom key row;
- Android IME;
- split-screen;
- orientation.

При изменении canvas:

```text
measure px → cell metrics → rows/cols → SSH window-change
```

Resize debounce должен быть коротким и не создавать лавину network calls.

## 13. Состояние при сворачивании

- terminal session остаётся в Foreground Service;
- UI buffer продолжает обновляться с контролем памяти;
- notification показывает количество активных sessions;
- возвращение в приложение открывает последнюю вкладку;
- после system process kill приложение восстанавливает metadata и reconnect/reattach к tmux, а не обещает сохранить локальный process.

## 14. Ошибки

Пользователь видит русское объяснение:

```text
Не удалось проверить ключ сервера
Сеть Tailscale недоступна
SSH-аутентификация отклонена
Сервер изменил SSH-ключ — подключение заблокировано
```

Кнопка `Технические детали` показывает исходное сообщение библиотеки/exception без перевода и без секретов.

## 15. Запрещённые UX-паттерны

- постоянная большая форма SSH над терминалом;
- ложный `ONLINE` до PTY READY;
- автоматическое принятие нового host key;
- автоматическая повторная отправка последней команды после reconnect;
- потеря terminal tab при rotation;
- использование WebView как terminal renderer;
- скрытая модификация shell output.

**ARCHITECTURE_STAGE_3 = COMPLETE**
