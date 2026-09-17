# Этап 26 — State/data contracts и persistence

Статус: ARCHITECTURE ONLY. APK не собирается.

## Цель

Зафиксировать модели данных до реализации, чтобы UI, transport, storage и tests могли развиваться параллельно.

## Основные сущности

### Machine

- id
- displayName
- type: VM/NUCBOX/PC
- tailscaleName
- capabilities
- trustState
- lastSeen
- healthSummary

### ConnectionProfile

- id
- machineId
- sshHost
- sshPort
- username
- credentialRef
- hostKeyFingerprint
- preferredWorkspaceId

Никаких raw private keys/password в этой модели.

### Workspace

- id
- machineId
- projectRoot
- displayName
- terminalTabs
- openFiles
- selectedGitBranch
- keyboardProfileId
- layoutState
- schemaVersion

### TerminalTab

- id
- workspaceId
- remoteSessionId
- tmuxSession
- tmuxWindow
- tmuxPane
- title
- cwdHint
- connectionState

### OpenFileState

- remotePath
- cursorLine
- cursorColumn
- remoteVersion/hash
- dirtyLocalDraftRef

### TestResultRef

- id
- workspaceId
- workingTreeFingerprint
- gateType
- status
- startedAt
- finishedAt
- summary

## State ownership

UI state != remote process state.

- UI state хранится локально.
- процессы принадлежат remote tmux.
- содержимое файлов принадлежит remote filesystem.
- credential material принадлежит secure credential store.
- control-plane truth принадлежит Gateway/Node state.

## Persistence

Локальная persistence должна быть транзакционной и версионируемой. Подход: Room/SQLite или эквивалентный typed persistence для workspace state + encrypted preferences для чувствительных ссылок/metadata.

## Migrations

Каждое изменение schemaVersion имеет migration test. Destructive migration для workspace state запрещена без export/backup fallback.

## Drafts

Несохранённый текст редактора хранится отдельно как draft с remote base hash. После восстановления сравниваются base hash и remote hash до merge/save.

## Serialization

Для API/local sync используются явные DTO/domain mappings. UI не работает напрямую с network DTO.

## Clock/time

Remote timestamps считаются информационными; конфликты файлов определяются не только временем, а hash/version metadata.

## Error model

Единый typed error contract:

- NetworkUnavailable
- GatewayUnavailable
- SshUnavailable
- AuthenticationFailed
- HostKeyChanged
- TrustRequired
- FileConflict
- PermissionDenied
- RemoteCommandFailed
- Timeout
- InternalInvariantViolation

UI переводит typed error в русское сообщение и отдельные технические детали.

## Gate

Contract tests проверяют serialization, migrations, conflict detection и отсутствие raw secrets в persisted models.

LIVE_TRADING_ENABLED=NO
RESEARCH_ONLY=YES
