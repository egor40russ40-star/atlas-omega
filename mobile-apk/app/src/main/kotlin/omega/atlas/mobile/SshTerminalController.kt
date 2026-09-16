package omega.atlas.mobile

import android.content.SharedPreferences
import android.util.Base64
import com.trilead.ssh2.Connection
import com.trilead.ssh2.ServerHostKeyVerifier
import com.trilead.ssh2.Session
import com.trilead.ssh2.StreamGobbler
import java.io.InputStream
import java.io.OutputStream
import java.security.MessageDigest
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.concurrent.thread

data class SshProfile(
    val host: String,
    val port: Int,
    val user: String,
    val password: String = "",
    val privateKeyPem: String = "",
    val privateKeyPassphrase: String = "",
)

sealed class TerminalConnectionState {
    data object Disconnected : TerminalConnectionState()
    data class Connecting(val message: String) : TerminalConnectionState()
    data class HostKeyPending(val fingerprint: String) : TerminalConnectionState()
    data class Connected(val endpoint: String) : TerminalConnectionState()
    data class Failed(val message: String) : TerminalConnectionState()
}

class SshTerminalController(
    private val prefs: SharedPreferences,
    private val onBytes: (ByteArray) -> Unit,
    private val onState: (TerminalConnectionState) -> Unit,
) {
    @Volatile private var connection: Connection? = null
    @Volatile private var session: Session? = null
    @Volatile private var stdin: OutputStream? = null
    @Volatile private var pendingFingerprint: String? = null
    @Volatile private var pendingHostKey: String? = null
    private val closing = AtomicBoolean(false)

    fun connect(profile: SshProfile) {
        disconnect(false)
        closing.set(false)
        onState(TerminalConnectionState.Connecting("Подключение к ${profile.user}@${profile.host}:${profile.port}"))

        thread(name = "atlas-ssh-connect", isDaemon = true) {
            try {
                val conn = Connection(profile.host, profile.port)
                connection = conn

                val verifier = ServerHostKeyVerifier { hostname, port, algorithm, serverHostKey ->
                    val fp = fingerprint(serverHostKey)
                    val key = fingerprintPreferenceKey(hostname, port, algorithm)
                    val trusted = prefs.getString(key, null)
                    when {
                        trusted == fp -> true
                        trusted != null -> {
                            onState(TerminalConnectionState.Failed("Ключ SSH-сервера изменился. Подключение заблокировано. Ожидался $trusted, получен $fp"))
                            false
                        }
                        else -> {
                            pendingFingerprint = fp
                            pendingHostKey = key
                            onState(TerminalConnectionState.HostKeyPending(fp))
                            false
                        }
                    }
                }

                conn.connect(verifier, 10_000, 15_000)
                if (closing.get()) return@thread

                val authenticated = when {
                    profile.privateKeyPem.isNotBlank() -> conn.authenticateWithPublicKey(
                        profile.user,
                        profile.privateKeyPem.toCharArray(),
                        profile.privateKeyPassphrase.ifBlank { null },
                    )
                    profile.password.isNotBlank() -> conn.authenticateWithPassword(profile.user, profile.password)
                    else -> conn.authenticateWithNone(profile.user)
                }

                if (!authenticated) error("SSH-аутентификация не выполнена. Укажите пароль или импортируйте приватный ключ.")

                val sshSession = conn.openSession()
                session = sshSession
                sshSession.requestPTY("xterm-256color", 80, 24, 0, 0, null)
                stdin = sshSession.stdin
                sshSession.startShell()

                onState(TerminalConnectionState.Connected("${profile.user}@${profile.host}"))
                startReader(StreamGobbler(sshSession.stdout), "stdout")
                startReader(StreamGobbler(sshSession.stderr), "stderr")
            } catch (e: Exception) {
                if (!closing.get() && pendingFingerprint == null) {
                    onState(TerminalConnectionState.Failed(e.message ?: e.javaClass.simpleName))
                }
                closeTransport()
            }
        }
    }

    fun trustPendingHostKey(): Boolean {
        val key = pendingHostKey ?: return false
        val fp = pendingFingerprint ?: return false
        prefs.edit().putString(key, fp).apply()
        pendingHostKey = null
        pendingFingerprint = null
        return true
    }

    fun send(data: ByteArray) {
        val out = stdin ?: return
        thread(name = "atlas-ssh-write", isDaemon = true) {
            try {
                synchronized(out) {
                    out.write(data)
                    out.flush()
                }
            } catch (e: Exception) {
                if (!closing.get()) onState(TerminalConnectionState.Failed("Ошибка отправки: ${e.message}"))
            }
        }
    }

    fun disconnect(report: Boolean = true) {
        closing.set(true)
        pendingFingerprint = null
        pendingHostKey = null
        closeTransport()
        if (report) onState(TerminalConnectionState.Disconnected)
    }

    private fun startReader(input: InputStream, name: String) {
        thread(name = "atlas-ssh-$name", isDaemon = true) {
            val buffer = ByteArray(16 * 1024)
            try {
                while (!closing.get()) {
                    val n = input.read(buffer)
                    if (n < 0) break
                    if (n > 0) onBytes(buffer.copyOf(n))
                }
                if (!closing.get()) onState(TerminalConnectionState.Disconnected)
            } catch (e: Exception) {
                if (!closing.get()) onState(TerminalConnectionState.Failed("SSH-поток завершён: ${e.message}"))
            } finally {
                closeTransport()
            }
        }
    }

    private fun closeTransport() {
        runCatching { stdin?.close() }
        runCatching { session?.close() }
        runCatching { connection?.close() }
        stdin = null
        session = null
        connection = null
    }

    private fun fingerprint(serverHostKey: ByteArray): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(serverHostKey)
        return "SHA256:" + Base64.encodeToString(digest, Base64.NO_WRAP or Base64.NO_PADDING)
    }

    private fun fingerprintPreferenceKey(host: String, port: Int, algorithm: String): String =
        "ssh_host_key::$host::$port::$algorithm"
}
