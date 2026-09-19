package omega.atlas.mobile.v2.transport.ssh

import com.trilead.ssh2.ChannelCondition
import com.trilead.ssh2.Connection
import com.trilead.ssh2.ServerHostKeyVerifier
import java.io.ByteArrayOutputStream
import java.io.InputStream
import kotlin.concurrent.thread
import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.result.AtlasError
import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.result.ErrorDomain
import omega.atlas.mobile.v2.core.result.TransportFailureClassifier
import omega.atlas.mobile.v2.core.security.CredentialVault
import omega.atlas.mobile.v2.core.security.HostKeyDecision
import omega.atlas.mobile.v2.core.security.HostKeyObservation
import omega.atlas.mobile.v2.core.security.HostKeyTrustPolicy
import omega.atlas.mobile.v2.core.security.SshCredential

data class SshCommandResult(
    val stdout: String,
    val stderr: String,
    val exitCode: Int,
    val outputTruncated: Boolean,
)

class TrileadCommandRunner(
    private val credentials: CredentialVault,
    private val trustPolicy: HostKeyTrustPolicy,
    private val timeoutMillis: Long = 20_000L,
    private val maxOutputBytes: Int = 2 * 1024 * 1024,
) {
    suspend fun run(
        profile: ConnectionProfile,
        command: String,
    ): AtlasResult<SshCommandResult> {
        require(command.isNotBlank()) { "Command must not be blank" }

        val credential = when (val loaded = credentials.loadSshCredential(profile.id)) {
            is AtlasResult.Success -> loaded.value
            is AtlasResult.Failure -> return loaded
        }

        var connection: Connection? = null
        var rejected: HostKeyObservation? = null
        return try {
            val conn = Connection(profile.host, profile.port)
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
                        rejected = observation
                        false
                    }
                }
            }
            conn.connect(verifier, 10_000, 15_000)

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
                return failure("ssh_exec_auth_failed", ErrorDomain.AUTH, "error_ssh_exec_auth_failed")
            }

            val session = conn.openSession()
            try {
                session.execCommand(command)
                val stdout = BoundedCollector(maxOutputBytes)
                val stderr = BoundedCollector(maxOutputBytes)
                val outThread = thread(name = "atlas-ssh-exec-out", isDaemon = true) {
                    stdout.readFrom(session.stdout)
                }
                val errThread = thread(name = "atlas-ssh-exec-err", isDaemon = true) {
                    stderr.readFrom(session.stderr)
                }

                val conditions = session.waitForCondition(
                    ChannelCondition.EXIT_STATUS or ChannelCondition.EOF or ChannelCondition.CLOSED,
                    timeoutMillis,
                )
                if ((conditions and ChannelCondition.TIMEOUT) != 0) {
                    session.close()
                    outThread.join(2_000)
                    errThread.join(2_000)
                    return failure(
                        "ssh_exec_timeout",
                        ErrorDomain.SSH,
                        "error_ssh_exec_timeout",
                        retryable = true,
                    )
                }

                outThread.join(2_000)
                errThread.join(2_000)
                val exit = session.exitStatus ?: -1
                AtlasResult.Success(
                    SshCommandResult(
                        stdout = stdout.text(),
                        stderr = stderr.text(),
                        exitCode = exit,
                        outputTruncated = stdout.truncated || stderr.truncated,
                    )
                )
            } finally {
                session.close()
            }
        } catch (e: Exception) {
            val observation = rejected
            if (observation != null) {
                failure(
                    "ssh_exec_host_key_blocked",
                    ErrorDomain.TRUST,
                    "error_ssh_exec_host_key_blocked",
                    "${observation.host}:${observation.port} ${observation.fingerprint}",
                    false,
                )
            } else {
                val classified = TransportFailureClassifier.classify(e)
                failure(
                    classified.code,
                    classified.domain,
                    "error_ssh_exec_failed",
                    e.javaClass.simpleName + ": " + (e.message ?: "transport"),
                    classified.retryable,
                )
            }
        } finally {
            runCatching { connection?.close() }
            wipeCredential(credential)
        }
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
        key: String,
        detail: String? = null,
        retryable: Boolean = false,
    ): AtlasResult<T> = AtlasResult.Failure(
        AtlasError(code, domain, key, detail, retryable)
    )

    private class BoundedCollector(private val limit: Int) {
        private val buffer = ByteArrayOutputStream(minOf(limit, 64 * 1024))
        @Volatile var truncated: Boolean = false
            private set

        fun readFrom(input: InputStream) {
            val chunk = ByteArray(16 * 1024)
            while (true) {
                val count = runCatching { input.read(chunk) }.getOrDefault(-1)
                if (count < 0) break
                if (count == 0) continue
                val remaining = limit - buffer.size()
                if (remaining > 0) {
                    buffer.write(chunk, 0, minOf(count, remaining))
                }
                if (count > remaining) truncated = true
            }
        }

        fun text(): String = buffer.toByteArray().toString(Charsets.UTF_8)
    }
}
