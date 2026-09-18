package omega.atlas.mobile.v2.app

import android.content.Context
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.TerminalLifecycleState
import omega.atlas.mobile.v2.core.model.TerminalSessionDescriptor
import omega.atlas.mobile.v2.core.model.TrustState
import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.security.HostKeyObservation
import omega.atlas.mobile.v2.core.security.PinnedHostKeyTrustPolicy
import omega.atlas.mobile.v2.core.security.SshCredential
import omega.atlas.mobile.v2.feature.files.AtomicTextWriteRequest
import omega.atlas.mobile.v2.feature.files.RemoteFileEntry
import omega.atlas.mobile.v2.feature.files.RemoteTextDocument
import omega.atlas.mobile.v2.feature.sessions.TerminalSessionCoordinator
import omega.atlas.mobile.v2.feature.terminal.TerminalSessionPort
import omega.atlas.mobile.v2.storage.local.AndroidKeystoreCredentialVault
import omega.atlas.mobile.v2.storage.local.SharedPreferencesConnectionProfileStore
import omega.atlas.mobile.v2.storage.local.SharedPreferencesHostKeyStore
import omega.atlas.mobile.v2.transport.sftp.TrileadRemoteFilesPort
import omega.atlas.mobile.v2.transport.ssh.TrileadTerminalSession
import org.connectbot.terminal.TerminalEmulator

data class EditorUiState(
    val path: String = "",
    val text: String = "",
    val dirty: Boolean = false,
    val loaded: Boolean = false,
    val saving: Boolean = false,
)

class AtlasTerminalRuntime(
    context: Context,
    private val emulator: TerminalEmulator,
) : TerminalSessionPort.Listener {

    private val appContext = context.applicationContext
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private val profileStore = SharedPreferencesConnectionProfileStore(appContext)
    private val vault = AndroidKeystoreCredentialVault(appContext)
    private val hostKeyPolicy = PinnedHostKeyTrustPolicy(SharedPreferencesHostKeyStore(appContext))
    private val transport = TrileadTerminalSession(vault, hostKeyPolicy)
    private val coordinator = TerminalSessionCoordinator(transport)

    private val _profile = mutableStateOf(profileStore.load() ?: defaultProfile())
    val profile: State<ConnectionProfile> = _profile

    private val _state = mutableStateOf(TerminalLifecycleState.DISCONNECTED)
    val state: State<TerminalLifecycleState> = _state

    private val _message = mutableStateOf("Готов к подключению")
    val message: State<String> = _message

    private val _pendingTrust = mutableStateOf<HostKeyObservation?>(null)
    val pendingTrust: State<HostKeyObservation?> = _pendingTrust

    private val _credentialStatus = mutableStateOf("Данные доступа хранятся в Android Keystore")
    val credentialStatus: State<String> = _credentialStatus

    private val _directoryPath = mutableStateOf(DEFAULT_WORKSPACE_ROOT)
    val directoryPath: State<String> = _directoryPath

    private val _files = mutableStateOf<List<RemoteFileEntry>>(emptyList())
    val files: State<List<RemoteFileEntry>> = _files

    private val _filesMessage = mutableStateOf("Нажмите «Обновить», чтобы загрузить файлы")
    val filesMessage: State<String> = _filesMessage

    private val _filesBusy = mutableStateOf(false)
    val filesBusy: State<Boolean> = _filesBusy

    private val _editor = mutableStateOf(EditorUiState())
    val editor: State<EditorUiState> = _editor

    private var editorDocument: RemoteTextDocument? = null

    init {
        transport.setListener(this)
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
                is AtlasResult.Success -> postMessage("Терминал подключён • tmux: atlas-mobile")
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

    fun saveProfile(
        title: String,
        host: String,
        port: Int,
        username: String,
        autoConnect: Boolean,
    ) {
        require(host.isNotBlank())
        require(username.isNotBlank())
        require(port in 1..65535)

        val previous = _profile.value
        val endpointChanged = previous.host != host.trim() || previous.port != port
        if (endpointChanged) {
            hostKeyPolicy.clear(previous.host, previous.port)
        }

        val updated = previous.copy(
            title = title.trim().ifBlank { "NucBox" },
            host = host.trim(),
            port = port,
            username = username.trim(),
            trustState = if (endpointChanged) TrustState.UNENROLLED else previous.trustState,
            autoConnect = autoConnect,
        )
        _profile.value = updated
        profileStore.save(updated)
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
        val normalized = normalizeRemotePath(path)
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
        val current = _directoryPath.value
        val parent = current.trimEnd('/').substringBeforeLast('/', missingDelimiterValue = "/").ifBlank { "/" }
        refreshFiles(parent)
    }

    fun openRemoteEntry(entry: RemoteFileEntry, onFileReady: () -> Unit = {}) {
        if (entry.directory) {
            refreshFiles(entry.path)
            return
        }
        scope.launch {
            _editor.value = EditorUiState(path = entry.path)
            _filesMessage.value = "Открытие ${entry.name}…"
        }
        scope.launch(Dispatchers.IO) {
            when (val result = remoteFilesPort().readText(entry.path)) {
                is AtlasResult.Success -> scope.launch {
                    editorDocument = result.value
                    _editor.value = EditorUiState(
                        path = result.value.snapshot.path,
                        text = result.value.text,
                        dirty = false,
                        loaded = true,
                    )
                    _filesMessage.value = "Файл открыт"
                    onFileReady()
                }
                is AtlasResult.Failure -> scope.launch {
                    _editor.value = EditorUiState(path = entry.path)
                    _filesMessage.value = filesErrorMessage(result.error.code, result.error.technicalDetail)
                }
            }
        }
    }

    fun updateEditorText(value: String) {
        val current = _editor.value
        if (!current.loaded) return
        _editor.value = current.copy(text = value, dirty = true)
    }

    fun saveEditor() {
        val current = _editor.value
        val document = editorDocument ?: return
        if (!current.loaded || !current.dirty || current.saving) return

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
                    _editor.value = current.copy(dirty = false, saving = false)
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

    private fun remoteFilesPort() = TrileadRemoteFilesPort(
        profile = _profile.value,
        credentials = vault,
        trustPolicy = hostKeyPolicy,
    )

    private fun normalizeRemotePath(value: String): String {
        val trimmed = value.trim()
        if (trimmed.isBlank()) return DEFAULT_WORKSPACE_ROOT
        return if (trimmed.length > 1) trimmed.trimEnd('/') else trimmed
    }

    private fun filesErrorMessage(code: String, detail: String?): String = when (code) {
        "file_changed_remotely" -> "Файл изменился на NucBox. Перезагрузите его перед сохранением."
        "file_too_large" -> "Файл слишком большой для мобильного редактора"
        "sftp_auth_failed" -> "SFTP: проверьте данные SSH-доступа"
        "sftp_host_key_blocked" -> "SFTP заблокирован: требуется подтверждение SSH-ключа"
        else -> "Ошибка файлов: ${detail ?: code}"
    }

    private fun userMessage(code: String, detail: String?): String = when (code) {
        "ssh_auth_failed" -> "Не удалось выполнить SSH-аутентификацию"
        "ssh_connect_failed" -> "Не удалось подключиться к SSH: ${detail ?: "сеть"}"
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
        trustState = TrustState.UNENROLLED,
        autoConnect = false,
    )

    private companion object {
        const val DEFAULT_WORKSPACE_ROOT = "/home/test4/ATLAS_EXECUTION_NODE"
    }
}
