package omega.atlas.mobile.v2.transport.ssh

import com.trilead.ssh2.Connection
import com.trilead.ssh2.ServerHostKeyVerifier
import com.trilead.ssh2.Session
import com.trilead.ssh2.StreamGobbler
import java.io.InputStream
import java.io.OutputStream
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.concurrent.thread
import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.SshEndpoint
import omega.atlas.mobile.v2.core.model.TerminalLifecycleState
import omega.atlas.mobile.v2.core.model.TerminalSessionDescriptor
import omega.atlas.mobile.v2.core.result.AtlasError
import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.result.ErrorDomain
import omega.atlas.mobile.v2.core.result.TransportFailureClassifier
import omega.atlas.mobile.v2.core.security.CredentialVault
import omega.atlas.mobile.v2.core.security.HostKeyDecision
import omega.atlas.mobile.v2.core.security.HostKeyObservation
import omega.atlas.mobile.v2.core.security.HostKeyTrustPolicy
import omega.atlas.mobile.v2.core.security.SshCredential
import omega.atlas.mobile.v2.feature.terminal.DeliveryCertainty
import omega.atlas.mobile.v2.feature.terminal.TerminalSessionPort
import omega.atlas.mobile.v2.feature.terminal.TerminalWriteReceipt

class TrileadTerminalSession(
    private val credentials: CredentialVault,
    private val trustPolicy: HostKeyTrustPolicy,
) : TerminalSessionPort {
    @Volatile private var connection: Connection? = null
    @Volatile private var session: Session? = null
    @Volatile private var stdin: OutputStream? = null
    @Volatile private var listener: TerminalSessionPort.Listener? = null
    @Volatile private var activeDescriptor: TerminalSessionDescriptor? = null
    @Volatile private var rejectedObservation: HostKeyObservation? = null
    @Volatile private var connectedEndpoint: SshEndpoint? = null
    private val closing = AtomicBoolean(false)

    override fun setListener(listener: TerminalSessionPort.Listener?) {
        this.listener = listener
    }

    fun pendingHostKeyObservation(): HostKeyObservation? = rejectedObservation

    fun activeEndpoint(): SshEndpoint? = connectedEndpoint

    fun clearPendingHostKeyObservation() {
        rejectedObservation = null
    }

    override suspend fun connect(
        profile: ConnectionProfile,
        session: TerminalSessionDescriptor,
    ): AtlasResult<Unit> {
        closeTransport()
        closing.set(false)
        activeDescriptor = session
        rejectedObservation = null
        listener?.onStateChanged(TerminalLifecycleState.CONNECTING)

        val credential = when (val loaded = credentials.loadSshCredential(profile.id)) {
            is AtlasResult.Success -> loaded.value
            is AtlasResult.Failure -> return loaded
        }

        var lastTransportFailure: AtlasResult.Failure? = null
        try {
            val endpoints = profile.sshEndpoints()
            for ((index, endpoint) in endpoints.withIndex()) {
                rejectedObservation = null
                connectedEndpoint = null
                try {
                    val conn = Connection(endpoint.host, endpoint.port)
                    connection = conn
                    val verifier = ServerHostKeyVerifier { host, port, algorithm, key ->
                        val observation = HostKeyObservation(
                            host = host,
                            port = port,
                            algorithm = algorithm,
                            fingerprint = SshTransportUtils.fingerprint(key),
                        )
                        when (trustPolicy.evaluate(observation)) {
                            HostKeyDecision.TRUSTED -> true
                            HostKeyDecision.UNSEEN,
                            HostKeyDecision.CHANGED -> {
                                rejectedObservation = observation
                                false
                            }
                        }
                    }

                    conn.connect(verifier, 10_000, 15_000)
                    listener?.onStateChanged(TerminalLifecycleState.AUTHENTICATING)

                    val authenticated = when (credential) {
                        SshCredential.None -> conn.authenticateWithNone(profile.username)
                        is SshCredential.Password -> conn.authenticateWithPassword(
                            profile.username,
                            credential.value.concatToString(),
                        )
                        is SshCredential.PrivateKey -> conn.authenticateWithPublicKey(
                            profile.username,
                            credential.pem,
                            credential.passphrase?.concatToString(),
                        )
                    }
                    if (!authenticated) {
                        closeTransport()
                        return failure("ssh_auth_failed", ErrorDomain.AUTH, "error_ssh_auth_failed")
                    }

                    listener?.onStateChanged(TerminalLifecycleState.OPENING_PTY)
                    val sshSession = conn.openSession()
                    this.session = sshSession
                    sshSession.requestPTY("xterm-256color", 80, 24, 0, 0, null)
                    stdin = sshSession.stdin
                    sshSession.startShell()
                    connectedEndpoint = endpoint
                    startReader(StreamGobbler(sshSession.stdout), "stdout")
                    startReader(StreamGobbler(sshSession.stderr), "stderr")
                    listener?.onStateChanged(TerminalLifecycleState.READY)
                    return AtlasResult.Success(Unit)
                } catch (e: Exception) {
                    val observation = rejectedObservation
                    closeTransport()
                    if (observation != null) {
                        return failure(
                            code = "ssh_host_key_blocked",
                            domain = ErrorDomain.TRUST,
                            messageKey = "error_ssh_host_key_blocked",
                            detail = "${observation.host}:${observation.port} ${observation.algorithm} ${observation.fingerprint}",
                        )
                    }

                    val classified = TransportFailureClassifier.classify(e)
                    val failure = failure<Unit>(
                        code = classified.code,
                        domain = classified.domain,
                        messageKey = "error_ssh_connect_failed",
                        detail = "${endpoint.label} ${endpoint.host}:${endpoint.port} • " +
                            e.javaClass.simpleName + ": " + (e.message ?: "transport"),
                        retryable = classified.retryable,
                    )
                    if (failure is AtlasResult.Failure) lastTransportFailure = failure

                    val mayFallback =
                        classified.domain == ErrorDomain.NETWORK &&
                            classified.retryable &&
                            index < endpoints.lastIndex
                    if (!mayFallback) return failure
                }
            }
            return lastTransportFailure
                ?: failure("network_transport_failed", ErrorDomain.NETWORK, "error_ssh_connect_failed")
        } finally {
            wipeCredential(credential)
        }
    }

    override suspend fun send(bytes: ByteArray): AtlasResult<TerminalWriteReceipt> {
        val out = stdin ?: return failure(
            "terminal_not_ready",
            ErrorDomain.PTY,
            "error_terminal_not_ready",
        )
        return try {
            synchronized(out) {
                out.write(bytes)
                out.flush()
            }
            AtlasResult.Success(TerminalWriteReceipt(bytes.size, DeliveryCertainty.DELIVERED))
        } catch (e: Exception) {
            failure(
                code = "terminal_delivery_unknown",
                domain = ErrorDomain.PTY,
                messageKey = "error_terminal_delivery_unknown",
                detail = e.message,
                retryable = false,
            )
        }
    }

    override suspend fun resize(columns: Int, rows: Int): AtlasResult<Unit> = try {
        require(columns > 0 && rows > 0)
        session?.resizePTY(columns, rows, 0, 0)
            ?: return failure("terminal_not_ready", ErrorDomain.PTY, "error_terminal_not_ready")
        AtlasResult.Success(Unit)
    } catch (e: Exception) {
        failure("pty_resize_failed", ErrorDomain.PTY, "error_pty_resize_failed", e.message, true)
    }

    override suspend fun detach(): AtlasResult<Unit> {
        closing.set(true)
        closeTransport()
        listener?.onStateChanged(TerminalLifecycleState.DISCONNECTED)
        return AtlasResult.Success(Unit)
    }

    override suspend fun closeRemoteSession(): AtlasResult<Unit> {
        val descriptor = activeDescriptor
            ?: return failure("terminal_not_ready", ErrorDomain.TMUX, "error_terminal_not_ready")
        val safeName = try {
            SshTransportUtils.requireSafeTmuxSessionName(descriptor.tmuxSessionName)
        } catch (e: IllegalArgumentException) {
            return failure("tmux_name_invalid", ErrorDomain.VALIDATION, "error_tmux_name_invalid")
        }
        return when (val sent = send("tmux kill-session -t $safeName\r".encodeToByteArray())) {
            is AtlasResult.Success -> AtlasResult.Success(Unit)
            is AtlasResult.Failure -> sent
        }
    }

    private fun startReader(input: InputStream, name: String) {
        thread(name = "atlas-v2-ssh-$name", isDaemon = true) {
            val buffer = ByteArray(16 * 1024)
            try {
                while (!closing.get()) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    if (count > 0) listener?.onOutput(buffer.copyOf(count))
                }
                if (!closing.get()) listener?.onStateChanged(TerminalLifecycleState.DISCONNECTED)
            } catch (_: Exception) {
                if (!closing.get()) listener?.onStateChanged(TerminalLifecycleState.ERROR)
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
        connectedEndpoint = null
    }

    private fun wipeCredential(credential: SshCredential) {
        when (credential) {
            SshCredential.None -> Unit
            is SshCredential.Password -> credential.value.fill('\u0000')
            is SshCredential.PrivateKey -> {
                credential.pem.fill('\u0000')
                credential.passphrase?.fill('\u0000')
            }
        }
    }

    private fun <T> failure(
        code: String,
        domain: ErrorDomain,
        messageKey: String,
        detail: String? = null,
        retryable: Boolean = false,
    ): AtlasResult<T> = AtlasResult.Failure(
        AtlasError(code, domain, messageKey, detail, retryable)
    )
}
