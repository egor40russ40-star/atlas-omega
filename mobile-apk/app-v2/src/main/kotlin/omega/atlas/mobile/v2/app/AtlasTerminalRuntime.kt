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
import omega.atlas.mobile.v2.feature.sessions.TerminalSessionCoordinator
import omega.atlas.mobile.v2.feature.terminal.TerminalSessionPort
import omega.atlas.mobile.v2.storage.local.AndroidKeystoreCredentialVault
import omega.atlas.mobile.v2.storage.local.SharedPreferencesConnectionProfileStore
import omega.atlas.mobile.v2.storage.local.SharedPreferencesHostKeyStore
import omega.atlas.mobile.v2.transport.ssh.TrileadTerminalSession
import org.connectbot.terminal.TerminalEmulator

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
}
