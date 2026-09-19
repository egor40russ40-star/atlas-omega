package omega.atlas.mobile.v2.app

import android.content.Context
import java.util.UUID
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.async
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.LayerStatus
import omega.atlas.mobile.v2.core.model.SshEndpoint
import omega.atlas.mobile.v2.core.model.SshEndpointKind
import omega.atlas.mobile.v2.core.model.TerminalLifecycleState
import omega.atlas.mobile.v2.core.model.TerminalSessionDescriptor
import omega.atlas.mobile.v2.core.model.TrustState
import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.result.ErrorDomain
import omega.atlas.mobile.v2.core.security.HostKeyObservation
import omega.atlas.mobile.v2.core.security.PinnedHostKeyTrustPolicy
import omega.atlas.mobile.v2.core.security.SshCredential
import omega.atlas.mobile.v2.feature.atlas.GatewayEndpointPolicy
import omega.atlas.mobile.v2.feature.atlas.GatewayVersion
import omega.atlas.mobile.v2.feature.files.AtomicTextWriteRequest
import omega.atlas.mobile.v2.feature.files.FileNavigationPolicy
import omega.atlas.mobile.v2.feature.files.RemoteFileEntry
import omega.atlas.mobile.v2.feature.files.RemoteTextDocument
import omega.atlas.mobile.v2.feature.files.WorkspacePathPolicy
import omega.atlas.mobile.v2.feature.editor.EditorHistory
import omega.atlas.mobile.v2.feature.git.GitSnapshot
import omega.atlas.mobile.v2.feature.sessions.TerminalSessionCoordinator
import omega.atlas.mobile.v2.feature.terminal.TerminalSessionPort
import omega.atlas.mobile.v2.storage.local.AndroidKeystoreCredentialVault
import omega.atlas.mobile.v2.storage.local.SharedPreferencesConnectionProfileStore
import omega.atlas.mobile.v2.storage.local.SharedPreferencesFileNavigationStore
import omega.atlas.mobile.v2.storage.local.SharedPreferencesHostKeyStore
import omega.atlas.mobile.v2.transport.gateway.HttpsGatewayStatusClient
import omega.atlas.mobile.v2.transport.sftp.TrileadRemoteFilesPort
import omega.atlas.mobile.v2.transport.ssh.TrileadCommandRunner
import omega.atlas.mobile.v2.transport.ssh.TrileadTerminalSession
import org.connectbot.terminal.TerminalEmulator

data class HealthProbeUi(
    val label: String,
    val status: LayerStatus,
    val detail: String,
    val technicalDetail: String? = null,
    val nextAction: String? = null,
)

data class EditorUiState(
    val path: String = "",
    val text: String = "",
    val dirty: Boolean = false,
    val loaded: Boolean = false,
    val saving: Boolean = false,
    val canUndo: Boolean = false,
    val canRedo: Boolean = false,
)

class AtlasTerminalRuntime(
    context: Context,
    private val emulator: TerminalEmulator,
) : TerminalSessionPort.Listener {

    private val appContext = context.applicationContext
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private val profileStore = SharedPreferencesConnectionProfileStore(appContext)
    private val fileNavigationStore = SharedPreferencesFileNavigationStore(appContext)
    private val vault = AndroidKeystoreCredentialVault(appContext)
    private val hostKeyPolicy = PinnedHostKeyTrustPolicy(SharedPreferencesHostKeyStore(appContext))
    private val transport = TrileadTerminalSession(vault, hostKeyPolicy)
    private val commandRunner = TrileadCommandRunner(vault, hostKeyPolicy)
    private val coordinator = TerminalSessionCoordinator(transport)
    private val gitRepository = SshGitRepository({ _profile.value }, commandRunner)
    private val gatewayClient = HttpsGatewayStatusClient()

    private val _profile = mutableStateOf(profileStore.load() ?: defaultProfile())
    val profile: State<ConnectionProfile> = _profile

    private val _profiles = mutableStateOf(profileStore.list().ifEmpty { listOf(_profile.value) })
    val profiles: State<List<ConnectionProfile>> = _profiles

    private val _state = mutableStateOf(TerminalLifecycleState.DISCONNECTED)
    val state: State<TerminalLifecycleState> = _state

    private val _message = mutableStateOf("Готов к подключению")
    val message: State<String> = _message

    private val _pendingTrust = mutableStateOf<HostKeyObservation?>(null)
    val pendingTrust: State<HostKeyObservation?> = _pendingTrust

    private val _credentialStatus = mutableStateOf("Данные доступа хранятся в Android Keystore")
    val credentialStatus: State<String> = _credentialStatus

    private val _directoryPath = mutableStateOf(_profile.value.workspaceRoot)
    val directoryPath: State<String> = _directoryPath

    private val _files = mutableStateOf<List<RemoteFileEntry>>(emptyList())
    val files: State<List<RemoteFileEntry>> = _files

    private val _filesMessage = mutableStateOf("Нажмите «Обновить», чтобы загрузить файлы")
    val filesMessage: State<String> = _filesMessage

    private val _filesBusy = mutableStateOf(false)
    val filesBusy: State<Boolean> = _filesBusy

    private val _fileFavorites = mutableStateOf<Set<String>>(emptySet())
    val fileFavorites: State<Set<String>> = _fileFavorites

    private val _recentFiles = mutableStateOf<List<String>>(emptyList())
    val recentFiles: State<List<String>> = _recentFiles

    private val _editor = mutableStateOf(EditorUiState())
    val editor: State<EditorUiState> = _editor

    private var editorDocument: RemoteTextDocument? = null
    private var editorHistory = EditorHistory("")

    private val _gitSnapshot = mutableStateOf(GitSnapshot(branch = "—"))
    val gitSnapshot: State<GitSnapshot> = _gitSnapshot

    private val _gitSelectedPath = mutableStateOf<String?>(null)
    val gitSelectedPath: State<String?> = _gitSelectedPath

    private val _gitDiff = mutableStateOf<String?>(null)
    val gitDiff: State<String?> = _gitDiff

    private val _gitMessage = mutableStateOf("Нажмите «Обновить Git»")
    val gitMessage: State<String> = _gitMessage

    private val _gitBusy = mutableStateOf(false)
    val gitBusy: State<Boolean> = _gitBusy

    private val _gatewayVersion = mutableStateOf<GatewayVersion?>(null)
    val gatewayVersion: State<GatewayVersion?> = _gatewayVersion

    private val _gatewayMessage = mutableStateOf("Нажмите «Проверить Gateway»")
    val gatewayMessage: State<String> = _gatewayMessage

    private val _gatewayBusy = mutableStateOf(false)
    val gatewayBusy: State<Boolean> = _gatewayBusy

    private val _healthProbes = mutableStateOf(defaultHealthProbes())
    val healthProbes: State<List<HealthProbeUi>> = _healthProbes

    private val _healthBusy = mutableStateOf(false)
    val healthBusy: State<Boolean> = _healthBusy

    private val _healthMessage = mutableStateOf("Диагностика ещё не запускалась")
    val healthMessage: State<String> = _healthMessage

    init {
        transport.setListener(this)
        reloadFileNavigation()
    }

    fun connect() {
        val current = _profile.value
        _message.value = "Подключение к ${current.username}@${current.host}…"
        _pendingTrust.value = null
        scope.launch(Dispatchers.IO) {
            val descriptor = TerminalSessionDescriptor(
                id = "mobile-main",
                workspaceId = "atlas-execution-node",
                connectionProfileId = current.id,
                tmuxSessionName = "atlas-mobile",
                title = "ATLAS",
            )
            when (val result = coordinator.open(current, descriptor)) {
                is AtlasResult.Success -> {
                    val endpoint = transport.activeEndpoint()
                    postMessage(
                        "Терминал подключён • " +
                            (endpoint?.let { "${it.label}: ${it.host}:${it.port}" } ?: current.host) +
                            " • tmux: atlas-mobile"
                    )
                }
                is AtlasResult.Failure -> {
                    val pending = transport.pendingHostKeyObservation()
                    if (pending != null) {
                        scope.launch {
                            _pendingTrust.value = pending
                            _state.value = TerminalLifecycleState.BLOCKED
                            _message.value = "Требуется подтверждение ключа SSH-сервера"
                        }
                    } else {
                        postState(TerminalLifecycleState.ERROR)
                        postMessage(userMessage(result.error.code, result.error.technicalDetail))
                    }
                }
            }
        }
    }

    fun trustAndReconnect() {
        val observation = _pendingTrust.value ?: return
        hostKeyPolicy.pin(observation)
        transport.clearPendingHostKeyObservation()
        val trusted = _profile.value.copy(trustState = TrustState.TRUSTED)
        _profile.value = trusted
        profileStore.save(trusted)
        _profiles.value = profileStore.list()
        _pendingTrust.value = null
        connect()
    }

    fun send(bytes: ByteArray) {
        if (bytes.isEmpty()) return
        scope.launch(Dispatchers.IO) {
            when (val result = transport.send(bytes)) {
                is AtlasResult.Success -> Unit
                is AtlasResult.Failure -> postMessage(
                    userMessage(result.error.code, result.error.technicalDetail)
                )
            }
        }
    }

    fun resize(columns: Int, rows: Int) {
        if (columns <= 0 || rows <= 0) return
        scope.launch(Dispatchers.IO) {
            transport.resize(columns, rows)
        }
    }

    fun disconnect() {
        scope.launch(Dispatchers.IO) {
            coordinator.detach()
            postState(TerminalLifecycleState.DISCONNECTED)
            postMessage("Отключено. Удалённая tmux-сессия сохранена.")
        }
    }

    fun beginNewProfile() {
        val draft = ConnectionProfile(
            id = "profile-" + UUID.randomUUID().toString(),
            title = "Новое подключение",
            host = "",
            port = 22,
            username = "",
            workspaceRoot = "/home",
            gatewayBaseUrl = DEFAULT_GATEWAY,
            trustState = TrustState.UNENROLLED,
            autoConnect = false,
        )
        applyActiveProfile(draft)
        _credentialStatus.value = "Для нового профиля данные доступа ещё не сохранены"
        _message.value = "Заполните новый профиль"
    }

    fun cancelProfileEdit() {
        if (profileStore.contains(_profile.value.id)) return
        val restored = profileStore.load() ?: defaultProfile()
        applyActiveProfile(restored)
        refreshCredentialStatus(restored.id)
        _message.value = "Создание профиля отменено"
    }

    fun selectProfile(
        id: String,
        connectAfterSelection: Boolean = false,
    ) {
        val selected = profileStore.select(id) ?: return
        scope.launch(Dispatchers.IO) {
            coordinator.detach()
            scope.launch {
                applyActiveProfile(selected)
                refreshCredentialStatus(selected.id)
                _message.value = "Активный профиль: ${selected.title}"
                if (connectAfterSelection) connect()
            }
        }
    }

    fun saveProfile(
        title: String,
        host: String,
        port: Int,
        username: String,
        fallbackHost: String,
        fallbackPort: Int,
        workspaceRoot: String,
        gatewayBaseUrl: String,
        autoConnect: Boolean,
    ) {
        require(host.isNotBlank())
        require(username.isNotBlank())
        require(port in 1..65535)
        require(fallbackPort in 1..65535)
        val normalizedWorkspaceRoot = normalizeWorkspaceRoot(workspaceRoot)
        val normalizedGateway = GatewayEndpointPolicy.normalizeHttpsBaseUrl(gatewayBaseUrl)

        val previous = _profile.value
        val endpointChanged = previous.host != host.trim() || previous.port != port
        val fallbackEndpoints = fallbackHost.trim()
            .takeIf { it.isNotBlank() }
            ?.let {
                listOf(
                    SshEndpoint(
                        id = "fallback-1",
                        label = "Резервный",
                        host = it,
                        port = fallbackPort,
                        kind = SshEndpointKind.FALLBACK,
                    )
                )
            }
            ?: emptyList()

        val updated = previous.copy(
            title = title.trim().ifBlank { "NucBox" },
            host = host.trim(),
            port = port,
            username = username.trim(),
            workspaceRoot = normalizedWorkspaceRoot,
            gatewayBaseUrl = normalizedGateway,
            trustState = if (endpointChanged) TrustState.UNENROLLED else previous.trustState,
            autoConnect = autoConnect,
            fallbackSshEndpoints = fallbackEndpoints,
        )
        _profile.value = updated
        profileStore.save(updated)
        _profiles.value = profileStore.list()
        if (previous.workspaceRoot != updated.workspaceRoot) {
            _directoryPath.value = updated.workspaceRoot
            _files.value = emptyList()
            _editor.value = EditorUiState()
            editorDocument = null
            editorHistory = EditorHistory("")
            _gitSnapshot.value = GitSnapshot(branch = "—")
            _gitSelectedPath.value = null
            _gitDiff.value = null
        }
        _message.value = "Профиль сохранён"
    }

    fun savePassword(password: String) {
        if (password.isEmpty()) return
        val chars = password.toCharArray()
        scope.launch(Dispatchers.IO) {
            try {
                when (val result = vault.saveSshCredential(
                    _profile.value.id,
                    SshCredential.Password(chars),
                )) {
                    is AtlasResult.Success -> postCredential("Пароль сохранён в Android Keystore")
                    is AtlasResult.Failure -> postCredential("Не удалось сохранить пароль")
                }
            } finally {
                chars.fill('\u0000')
            }
        }
    }

    fun savePrivateKey(pem: String, passphrase: String?) {
        val keyChars = pem.toCharArray()
        val passChars = passphrase?.takeIf { it.isNotBlank() }?.toCharArray()
        scope.launch(Dispatchers.IO) {
            try {
                when (val result = vault.saveSshCredential(
                    _profile.value.id,
                    SshCredential.PrivateKey(keyChars, passChars),
                )) {
                    is AtlasResult.Success -> postCredential("SSH-ключ сохранён в Android Keystore")
                    is AtlasResult.Failure -> postCredential("Не удалось сохранить SSH-ключ")
                }
            } finally {
                keyChars.fill('\u0000')
                passChars?.fill('\u0000')
            }
        }
    }

    fun removeCredential() {
        scope.launch(Dispatchers.IO) {
            vault.removeSshCredential(_profile.value.id)
            postCredential("Данные доступа удалены")
        }
    }

    fun refreshFiles(path: String = _directoryPath.value) {
        val normalized = try {
            WorkspacePathPolicy.resolve(currentWorkspaceRoot(), path)
        } catch (_: IllegalArgumentException) {
            _filesMessage.value = "Путь вне разрешённого workspace заблокирован"
            return
        }
        scope.launch {
            _filesBusy.value = true
            _filesMessage.value = "Загрузка…"
        }
        scope.launch(Dispatchers.IO) {
            when (val result = remoteFilesPort().list(normalized)) {
                is AtlasResult.Success -> scope.launch {
                    _directoryPath.value = normalized
                    _files.value = result.value
                    _filesMessage.value = "${result.value.size} объектов"
                    _filesBusy.value = false
                }
                is AtlasResult.Failure -> scope.launch {
                    _filesMessage.value = filesErrorMessage(result.error.code, result.error.technicalDetail)
                    _filesBusy.value = false
                }
            }
        }
    }

    fun openParentDirectory() {
        refreshFiles(
            WorkspacePathPolicy.parent(
                root = currentWorkspaceRoot(),
                current = _directoryPath.value,
            )
        )
    }

    fun openRemoteEntry(entry: RemoteFileEntry, onFileReady: () -> Unit = {}) {
        val safePath = try {
            WorkspacePathPolicy.resolve(currentWorkspaceRoot(), entry.path)
        } catch (_: IllegalArgumentException) {
            _filesMessage.value = "Открытие вне разрешённого workspace заблокировано"
            return
        }
        if (entry.directory) {
            refreshFiles(safePath)
            return
        }
        scope.launch {
            _editor.value = EditorUiState(path = safePath)
            _filesMessage.value = "Открытие ${entry.name}…"
        }
        scope.launch(Dispatchers.IO) {
            when (val result = remoteFilesPort().readText(safePath)) {
                is AtlasResult.Success -> scope.launch {
                    editorDocument = result.value
                    editorHistory = EditorHistory(result.value.text)
                    _editor.value = EditorUiState(
                        path = result.value.snapshot.path,
                        text = result.value.text,
                        dirty = false,
                        loaded = true,
                        canUndo = false,
                        canRedo = false,
                    )
                    _filesMessage.value = "Файл открыт"
                    recordRecentFile(result.value.snapshot.path)
                    onFileReady()
                }
                is AtlasResult.Failure -> scope.launch {
                    _editor.value = EditorUiState(path = safePath)
                    _filesMessage.value = filesErrorMessage(result.error.code, result.error.technicalDetail)
                }
            }
        }
    }

    fun toggleFavoriteDirectory(path: String = _directoryPath.value) {
        val safe = runCatching {
            WorkspacePathPolicy.resolve(currentWorkspaceRoot(), path)
        }.getOrNull() ?: return
        val next = FileNavigationPolicy.toggleFavorite(
            favorites = _fileFavorites.value,
            path = safe,
            maxFavorites = MAX_FILE_FAVORITES,
        )
        _fileFavorites.value = next
        fileNavigationStore.saveFavorites(_profile.value.id, next)
    }

    fun openFavoriteDirectory(path: String) {
        if (WorkspacePathPolicy.isWithin(currentWorkspaceRoot(), path)) {
            refreshFiles(path)
        }
    }

    fun openRecentFile(path: String, onFileReady: () -> Unit = {}) {
        if (!WorkspacePathPolicy.isWithin(currentWorkspaceRoot(), path)) {
            _recentFiles.value = _recentFiles.value.filterNot { it == path }
            fileNavigationStore.saveRecent(_profile.value.id, _recentFiles.value)
            _filesMessage.value = "Недавний файл больше не принадлежит workspace"
            return
        }
        openRemoteEntry(
            RemoteFileEntry(
                path = path,
                name = path.substringAfterLast('/').ifBlank { path },
                directory = false,
                sizeBytes = 0L,
                modifiedEpochMillis = 0L,
            ),
            onFileReady,
        )
    }

    fun clearRecentFiles() {
        _recentFiles.value = emptyList()
        fileNavigationStore.saveRecent(_profile.value.id, emptyList())
    }

    fun updateEditorText(value: String) {
        val current = _editor.value
        if (!current.loaded || current.text == value) return
        editorHistory.record(value)
        val baseline = editorDocument?.text.orEmpty()
        _editor.value = current.copy(
            text = value,
            dirty = value != baseline,
            canUndo = editorHistory.canUndo,
            canRedo = editorHistory.canRedo,
        )
    }

    fun undoEditor() {
        val current = _editor.value
        if (!current.loaded) return
        val next = editorHistory.undo() ?: return
        val baseline = editorDocument?.text.orEmpty()
        _editor.value = current.copy(
            text = next,
            dirty = next != baseline,
            canUndo = editorHistory.canUndo,
            canRedo = editorHistory.canRedo,
        )
    }

    fun redoEditor() {
        val current = _editor.value
        if (!current.loaded) return
        val next = editorHistory.redo() ?: return
        val baseline = editorDocument?.text.orEmpty()
        _editor.value = current.copy(
            text = next,
            dirty = next != baseline,
            canUndo = editorHistory.canUndo,
            canRedo = editorHistory.canRedo,
        )
    }

    fun saveEditor() {
        val current = _editor.value
        val document = editorDocument ?: return
        if (!current.loaded || !current.dirty || current.saving) return
        if (!WorkspacePathPolicy.isWithin(currentWorkspaceRoot(), current.path)) {
            _filesMessage.value = "Сохранение вне разрешённого workspace заблокировано"
            return
        }

        _editor.value = current.copy(saving = true)
        scope.launch(Dispatchers.IO) {
            val request = AtomicTextWriteRequest(
                path = current.path,
                text = current.text,
                expectedSnapshot = document.snapshot,
            )
            when (val result = remoteFilesPort().writeTextAtomic(request)) {
                is AtlasResult.Success -> scope.launch {
                    editorDocument = RemoteTextDocument(
                        snapshot = result.value,
                        text = current.text,
                    )
                    _editor.value = current.copy(
                        dirty = false,
                        saving = false,
                        canUndo = editorHistory.canUndo,
                        canRedo = editorHistory.canRedo,
                    )
                    _filesMessage.value = "Сохранено безопасно"
                    refreshFiles(_directoryPath.value)
                }
                is AtlasResult.Failure -> scope.launch {
                    _editor.value = current.copy(saving = false)
                    _filesMessage.value = filesErrorMessage(result.error.code, result.error.technicalDetail)
                }
            }
        }
    }

    fun insertEditorIntoTerminal(execute: Boolean) {
        val current = _editor.value
        if (!current.loaded || current.text.isEmpty()) return
        val payload = if (execute) {
            current.text.trimEnd() + "\n"
        } else {
            current.text
        }
        send(payload.encodeToByteArray())
    }

    fun runHealthCheck() {
        if (_healthBusy.value) return
        scope.launch {
            _healthBusy.value = true
            _healthMessage.value = "Параллельная проверка слоёв…"
            _healthProbes.value = defaultHealthProbes().map {
                it.copy(status = LayerStatus.CHECKING, detail = "Проверка…")
            }
        }

        scope.launch(Dispatchers.IO) {
            val profile = _profile.value
            val gatewayDeferred = async {
                gatewayClient.version(profile.gatewayBaseUrl ?: DEFAULT_GATEWAY)
            }
            val sshDeferred = async {
                commandRunner.run(profile, "printf ATLAS_MOBILE_OK")
            }
            val sftpDeferred = async {
                remoteFilesPort().list(currentWorkspaceRoot())
            }
            val gitDeferred = async {
                gitRepository.status(currentWorkspaceRoot())
            }

            val gateway = gatewayDeferred.await()
            val ssh = sshDeferred.await()
            val sftp = sftpDeferred.await()
            val git = gitDeferred.await()

            val probes = listOf(
                probe(
                    label = "Gateway",
                    result = gateway,
                    successDetail = {
                        "${it.version} • ${it.mode} • authority=${it.liveTradingAuthority}"
                    },
                ),
                probe(
                    label = "SSH",
                    result = ssh,
                    successDetail = {
                        if (it.exitCode == 0 && it.stdout.contains("ATLAS_MOBILE_OK")) "Командный канал готов"
                        else "Неожиданный ответ SSH"
                    },
                ),
                probe(
                    label = "SFTP",
                    result = sftp,
                    successDetail = { "${it.size} объектов в корне проекта" },
                ),
                probe(
                    label = "Git",
                    result = git,
                    successDetail = {
                        if (it.isClean) "Ветка ${it.branch} • чисто"
                        else "Ветка ${it.branch} • ${it.changes.size} изменений"
                    },
                ),
                terminalProbe(),
            )

            scope.launch {
                _healthProbes.value = probes
                val ready = probes.count { it.status == LayerStatus.READY }
                val blocked = probes.count { it.status == LayerStatus.BLOCKED }
                _healthMessage.value = "Готово: $ready/${probes.size} READY" +
                    if (blocked > 0) " • требуется действие: $blocked" else ""
                _healthBusy.value = false
            }
        }
    }

    private fun <T> probe(
        label: String,
        result: AtlasResult<T>,
        successDetail: (T) -> String,
    ): HealthProbeUi = when (result) {
        is AtlasResult.Success -> HealthProbeUi(label, LayerStatus.READY, successDetail(result.value))
        is AtlasResult.Failure -> {
            val status = when (result.error.domain) {
                ErrorDomain.TRUST,
                ErrorDomain.AUTH -> LayerStatus.BLOCKED
                ErrorDomain.NETWORK -> LayerStatus.OFFLINE
                else -> LayerStatus.DEGRADED
            }
            HealthProbeUi(
                label = label,
                status = status,
                detail = diagnosticSummary(result.error.code),
                technicalDetail = result.error.technicalDetail
                    ?.lineSequence()
                    ?.firstOrNull()
                    ?.take(240),
                nextAction = diagnosticNextAction(result.error.code),
            )
        }
    }

    private fun terminalProbe(): HealthProbeUi {
        val current = _state.value
        val status = when (current) {
            TerminalLifecycleState.READY -> LayerStatus.READY
            TerminalLifecycleState.BLOCKED -> LayerStatus.BLOCKED
            TerminalLifecycleState.ERROR -> LayerStatus.DEGRADED
            TerminalLifecycleState.CONNECTING,
            TerminalLifecycleState.AUTHENTICATING,
            TerminalLifecycleState.OPENING_PTY,
            TerminalLifecycleState.ATTACHING_TMUX,
            TerminalLifecycleState.RECONNECTING -> LayerStatus.CHECKING
            TerminalLifecycleState.DISCONNECTED -> LayerStatus.UNKNOWN
        }
        return HealthProbeUi("Terminal/tmux", status, userMessageForTerminalState(current))
    }

    private fun userMessageForTerminalState(state: TerminalLifecycleState): String = when (state) {
        TerminalLifecycleState.READY -> "PTY/tmux рабочая сессия активна"
        TerminalLifecycleState.BLOCKED -> "Требуется подтверждение доверия"
        TerminalLifecycleState.ERROR -> "Последняя терминальная операция завершилась ошибкой"
        TerminalLifecycleState.DISCONNECTED -> "Терминал не подключён"
        else -> "Терминал выполняет переход состояния"
    }

    fun refreshGateway() {
        val baseUrl = _profile.value.gatewayBaseUrl ?: DEFAULT_GATEWAY
        scope.launch {
            _gatewayBusy.value = true
            _gatewayMessage.value = "Проверка Gateway…"
        }
        scope.launch(Dispatchers.IO) {
            when (val result = gatewayClient.version(baseUrl)) {
                is AtlasResult.Success -> scope.launch {
                    _gatewayVersion.value = result.value
                    _gatewayMessage.value = if (result.value.liveTradingAuthorityAbsent) {
                        "Gateway доступен • live authority отсутствует"
                    } else {
                        "ВНИМАНИЕ: Gateway сообщает live authority = ${result.value.liveTradingAuthority}"
                    }
                    _gatewayBusy.value = false
                }
                is AtlasResult.Failure -> scope.launch {
                    _gatewayVersion.value = null
                    _gatewayMessage.value = "Gateway: " + diagnosticSummary(result.error.code)
                    _gatewayBusy.value = false
                }
            }
        }
    }

    fun refreshGit() {
        scope.launch { _gitBusy.value = true; _gitMessage.value = "Чтение Git status…" }
        scope.launch(Dispatchers.IO) {
            when (val result = gitRepository.status(currentWorkspaceRoot())) {
                is AtlasResult.Success -> scope.launch {
                    _gitSnapshot.value = result.value
                    _gitMessage.value = if (result.value.isClean) "Рабочее дерево чистое" else "${result.value.changes.size} изменений"
                    _gitBusy.value = false
                }
                is AtlasResult.Failure -> scope.launch {
                    _gitMessage.value = gitErrorMessage(result.error.technicalDetail)
                    _gitBusy.value = false
                }
            }
        }
    }

    fun selectGitPath(path: String) {
        _gitSelectedPath.value = path
        _gitDiff.value = "Загрузка diff…"
        scope.launch(Dispatchers.IO) {
            when (val result = gitRepository.diff(currentWorkspaceRoot(), path)) {
                is AtlasResult.Success -> scope.launch { _gitDiff.value = result.value.unifiedDiff }
                is AtlasResult.Failure -> scope.launch { _gitDiff.value = gitErrorMessage(result.error.technicalDetail) }
            }
        }
    }

    fun stageGit(path: String) {
        gitMutation("Добавление в stage…") { gitRepository.stage(currentWorkspaceRoot(), path) }
    }

    fun unstageGit(path: String) {
        gitMutation("Удаление из stage…") { gitRepository.unstage(currentWorkspaceRoot(), path) }
    }

    fun commitGit(message: String) {
        scope.launch { _gitBusy.value = true; _gitMessage.value = "Создание commit…" }
        scope.launch(Dispatchers.IO) {
            when (val result = gitRepository.commit(currentWorkspaceRoot(), message)) {
                is AtlasResult.Success -> scope.launch {
                    _gitMessage.value = "Commit создан: ${result.value.take(12)}"
                    _gitBusy.value = false
                    refreshGit()
                }
                is AtlasResult.Failure -> scope.launch {
                    _gitMessage.value = gitErrorMessage(result.error.technicalDetail)
                    _gitBusy.value = false
                }
            }
        }
    }

    private fun gitMutation(label: String, action: suspend () -> AtlasResult<Unit>) {
        scope.launch { _gitBusy.value = true; _gitMessage.value = label }
        scope.launch(Dispatchers.IO) {
            when (val result = action()) {
                is AtlasResult.Success -> scope.launch {
                    _gitBusy.value = false
                    refreshGit()
                }
                is AtlasResult.Failure -> scope.launch {
                    _gitMessage.value = gitErrorMessage(result.error.technicalDetail)
                    _gitBusy.value = false
                }
            }
        }
    }

    override fun onStateChanged(state: TerminalLifecycleState) {
        postState(state)
        if (state == TerminalLifecycleState.READY) {
            postMessage("SSH/PTy готов • восстанавливается tmux")
        }
    }

    override fun onOutput(bytes: ByteArray) {
        emulator.writeInput(bytes)
    }

    fun close() {
        transport.setListener(null)
        scope.launch(Dispatchers.IO) { coordinator.detach() }
        scope.cancel()
    }

    private fun postState(value: TerminalLifecycleState) {
        scope.launch { _state.value = value }
    }

    private fun postMessage(value: String) {
        scope.launch { _message.value = value }
    }

    private fun postCredential(value: String) {
        scope.launch { _credentialStatus.value = value }
    }

    private fun applyActiveProfile(profile: ConnectionProfile) {
        _profile.value = profile
        _directoryPath.value = profile.workspaceRoot
        _files.value = emptyList()
        _filesMessage.value = "Нажмите «Обновить», чтобы загрузить файлы"
        _editor.value = EditorUiState()
        editorDocument = null
        editorHistory = EditorHistory("")
        _gitSnapshot.value = GitSnapshot(branch = "—")
        _gitSelectedPath.value = null
        _gitDiff.value = null
        _gitMessage.value = "Нажмите «Обновить Git»"
        _gatewayVersion.value = null
        _gatewayMessage.value = "Нажмите «Проверить Gateway»"
        _pendingTrust.value = null
        _state.value = TerminalLifecycleState.DISCONNECTED
        reloadFileNavigation()
    }

    private fun reloadFileNavigation() {
        val profile = _profile.value
        val root = profile.workspaceRoot
        val favorites = fileNavigationStore.loadFavorites(profile.id)
            .filterTo(linkedSetOf()) { WorkspacePathPolicy.isWithin(root, it) }
        val recent = fileNavigationStore.loadRecent(profile.id)
            .filter { WorkspacePathPolicy.isWithin(root, it) }
            .let { FileNavigationPolicy.normalizeRecent(it, MAX_RECENT_FILES) }
        _fileFavorites.value = favorites
        _recentFiles.value = recent
    }

    private fun recordRecentFile(path: String) {
        if (!WorkspacePathPolicy.isWithin(currentWorkspaceRoot(), path)) return
        val next = FileNavigationPolicy.pushRecent(
            current = _recentFiles.value,
            path = path,
            maxItems = MAX_RECENT_FILES,
        )
        _recentFiles.value = next
        fileNavigationStore.saveRecent(_profile.value.id, next)
    }

    private fun refreshCredentialStatus(profileId: String) {
        scope.launch(Dispatchers.IO) {
            val label = when (val loaded = vault.loadSshCredential(profileId)) {
                is AtlasResult.Success -> when (loaded.value) {
                    SshCredential.None -> "Данные доступа для профиля не сохранены"
                    is SshCredential.Password -> "SSH-пароль сохранён в Android Keystore"
                    is SshCredential.PrivateKey -> "SSH-ключ сохранён в Android Keystore"
                }
                is AtlasResult.Failure -> "Не удалось прочитать защищённые данные доступа"
            }
            postCredential(label)
        }
    }

    private fun remoteFilesPort() = TrileadRemoteFilesPort(
        profile = _profile.value,
        credentials = vault,
        trustPolicy = hostKeyPolicy,
    )

    private fun currentWorkspaceRoot(): String = _profile.value.workspaceRoot

    private fun normalizeWorkspaceRoot(value: String): String {
        val normalized = value.trim().let {
            if (it.length > 1) it.trimEnd('/') else it
        }
        require(normalized.startsWith('/')) { "Workspace root must be an absolute path" }
        return normalized
    }

    private fun normalizeRemotePath(value: String): String {
        val trimmed = value.trim()
        if (trimmed.isBlank()) return currentWorkspaceRoot()
        return if (trimmed.length > 1) trimmed.trimEnd('/') else trimmed
    }

    private fun filesErrorMessage(code: String, detail: String?): String = when (code) {
        "file_changed_remotely" -> "Файл изменился на NucBox. Перезагрузите его перед сохранением."
        "file_too_large" -> "Файл слишком большой для мобильного редактора"
        "file_outside_workspace" -> "Доступ вне разрешённого workspace заблокирован"
        "sftp_auth_failed" -> "SFTP: проверьте данные SSH-доступа"
        "sftp_host_key_blocked" -> "SFTP заблокирован: требуется подтверждение SSH-ключа"
        else -> "Ошибка файлов: ${detail ?: code}"
    }

    private fun defaultHealthProbes(): List<HealthProbeUi> = listOf(
        HealthProbeUi("Gateway", LayerStatus.UNKNOWN, "Не проверено"),
        HealthProbeUi("SSH", LayerStatus.UNKNOWN, "Не проверено"),
        HealthProbeUi("SFTP", LayerStatus.UNKNOWN, "Не проверено"),
        HealthProbeUi("Git", LayerStatus.UNKNOWN, "Не проверено"),
        HealthProbeUi("Terminal/tmux", LayerStatus.UNKNOWN, "Не проверено"),
    )

    private fun gitErrorMessage(detail: String?): String =
        "Git: " + (detail?.lineSequence()?.firstOrNull()?.take(220) ?: "операция не выполнена")

    private fun diagnosticSummary(code: String): String = when (code) {
        "network_dns_failed" -> "Имя сервера не разрешается DNS"
        "network_route_unavailable" -> "Нет сетевого маршрута до сервера"
        "network_timeout" -> "Сервер не ответил за отведённое время"
        "network_connection_refused" -> "Сервер доступен, но порт отклонил соединение"
        "network_remote_closed" -> "Удалённая сторона закрыла соединение до завершения протокола"
        "network_tls_failed" -> "Защищённое TLS-соединение не прошло проверку"
        "network_transport_failed" -> "Сетевой транспорт не установил соединение"
        "ssh_exec_host_key_blocked",
        "ssh_host_key_blocked" -> "Требуется проверка SSH host key"
        "ssh_exec_auth_failed",
        "ssh_auth_failed" -> "SSH-аутентификация отклонена"
        "sftp_auth_failed" -> "SFTP-аутентификация отклонена"
        else -> "Проверка завершилась ошибкой: $code"
    }

    private fun diagnosticNextAction(code: String): String? = when (code) {
        "network_dns_failed" -> "Проверьте DNS/MagicDNS или выберите другой подтверждённый endpoint."
        "network_route_unavailable" -> "Проверьте сеть/VPN/маршрут до выбранной машины."
        "network_timeout" -> "Проверьте, включена ли машина и доступен ли выбранный маршрут."
        "network_connection_refused" -> "Проверьте, слушает ли целевой сервис нужный порт."
        "network_remote_closed" -> "TCP доступен; проверьте SSH/ACL/серверные ограничения на целевой машине."
        "network_tls_failed" -> "Не обходите проверку TLS. Проверьте имя хоста и сертификат."
        "ssh_exec_host_key_blocked",
        "ssh_host_key_blocked" -> "Сверьте SHA-256 fingerprint перед подтверждением доверия."
        "ssh_exec_auth_failed",
        "ssh_auth_failed",
        "sftp_auth_failed" -> "Проверьте credential именно этого профиля."
        else -> null
    }

    private fun userMessage(code: String, detail: String?): String = when (code) {
        "ssh_auth_failed" -> "Не удалось выполнить SSH-аутентификацию"
        "ssh_connect_failed" -> "Не удалось подключиться к SSH: ${detail ?: "сеть"}"
        "network_dns_failed",
        "network_route_unavailable",
        "network_timeout",
        "network_connection_refused",
        "network_remote_closed",
        "network_tls_failed",
        "network_transport_failed" -> diagnosticSummary(code)
        "terminal_delivery_unknown" -> "Связь прервалась во время отправки. Команда не будет повторена автоматически."
        "tmux_attach_delivery_unknown" -> "Неясно, дошла ли команда восстановления tmux. Автоповтор отключён."
        else -> "Ошибка: ${detail ?: code}"
    }

    private fun defaultProfile() = ConnectionProfile(
        id = "nucbox-primary",
        title = "NucBox",
        host = "atlas-omega-nucbox.tailf87948.ts.net",
        port = 22,
        username = "test4",
        gatewayBaseUrl = DEFAULT_GATEWAY,
        trustState = TrustState.UNENROLLED,
        autoConnect = false,
    )

    private companion object {
        const val MAX_FILE_FAVORITES = 12
        const val MAX_RECENT_FILES = 12
        const val DEFAULT_WORKSPACE_ROOT = "/home/test4/ATLAS_EXECUTION_NODE"
        const val DEFAULT_GATEWAY = "https://tinvest-robot.tailf87948.ts.net"
    }
}
