# Этап 22 — Производительность, сеть и энергопотребление

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

ATLAS Mobile должен оставаться быстрым при длительной терминальной работе, не перегревать телефон и не расходовать трафик/батарею из-за избыточного polling или перерисовок.

## Terminal rendering

- рендерить только видимый viewport + bounded scrollback;
- batching входящего PTY output;
- coalescing частых redraw;
- не пересобирать Compose hierarchy на каждый байт вывода;
- отдельный terminal rendering state от остального UI;
- измерять frame time/jank при `yes`, build logs, pytest и больших traceback.

## Backpressure

SSH reader не должен бесконтрольно накапливать данные в RAM. Вводится bounded queue и backpressure между transport -> emulator -> renderer.

При отставании UI приоритет — сохранение корректности потока, а не отображение каждого промежуточного кадра.

## Scrollback

Scrollback имеет конфигурируемый предел по строкам/памяти. Старые строки могут выгружаться в компактный локальный буфер. Unlimited RAM growth запрещён.

## Network strategy

Событийные каналы предпочтительнее polling:

- SSH/PTTY — streaming;
- Gateway — WebSocket/SSE там, где это оправдано;
- polling health — только fallback и с adaptive interval.

В foreground проверки чаще; в background — реже. При проблеме сеть проверяется быстро, но после стабильного состояния частота снижается.

## Reconnect

Используется jittered exponential backoff с верхним пределом. При возвращении connectivity выполняется ускоренная попытка reconnect. Auth/host-key failures не повторяются бесконечно.

## Battery

Foreground service разрешён только для активной terminal/workspace session. Если пользователь завершил все активные сессии — сервис останавливается.

Wake lock используется минимально и только если реально нужен для активного I/O. Постоянный wake lock запрещён.

## Data usage

- не передавать повторно terminal history после reconnect, если remote/session protocol позволяет resume;
- кэшировать неизменившиеся file metadata;
- большие файлы загружать chunked/on-demand;
- diff вместо полной передачи файла там, где безопасно и проще проверить;
- диагностика/логи имеют лимиты размера.

## Startup

Cold start не ждёт сеть блокирующе. Сначала отображается UI и сохранённый workspace, затем параллельно стартуют network/control/SSH checks.

## Performance budgets

Целевые бюджеты для acceptance:

- первый интерактивный экран: < 1.5 сек на целевом устройстве при тёплом storage;
- открытие локально сохранённого workspace: < 500 мс;
- terminal key -> local echo/remote response ощущается без заметной UI задержки;
- отсутствие sustained jank при типичном build output;
- память terminal session bounded и измеряется stress-test'ом.

## Profiling

В debug/dev builds собираются timing metrics по startup, SSH connect, tmux attach, file open, diff render и terminal throughput. Release не отправляет эти данные наружу автоматически.

## Gate

Performance regression считается блокирующей, если превышен memory budget, появляются ANR, terminal input lag или unbounded network retry.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
