package omega.atlas.mobile.v2.transport.sftp

import com.trilead.ssh2.Connection
import com.trilead.ssh2.ServerHostKeyVerifier
import com.trilead.ssh2.SFTPv3Client
import com.trilead.ssh2.SFTPv3DirectoryEntry
import java.io.ByteArrayOutputStream
import java.security.MessageDigest
import java.util.Base64
import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.RemoteFileSnapshot
import omega.atlas.mobile.v2.core.result.AtlasError
import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.result.ErrorDomain
import omega.atlas.mobile.v2.core.result.TransportFailureClassifier
import omega.atlas.mobile.v2.core.security.CredentialVault
import omega.atlas.mobile.v2.core.security.HostKeyDecision
import omega.atlas.mobile.v2.core.security.HostKeyObservation
import omega.atlas.mobile.v2.core.security.HostKeyTrustPolicy
import omega.atlas.mobile.v2.core.security.SshCredential
import omega.atlas.mobile.v2.feature.files.AtomicTextWriteRequest
import omega.atlas.mobile.v2.feature.files.RemoteFileEntry
import omega.atlas.mobile.v2.feature.files.RemoteFilesPort
import omega.atlas.mobile.v2.feature.files.RemoteTextDocument

class TrileadRemoteFilesPort(
    private val profile: ConnectionProfile,
    private val credentials: CredentialVault,
    private val trustPolicy: HostKeyTrustPolicy,
    private val maxTextBytes: Long = 4L * 1024L * 1024L,
) : RemoteFilesPort {

    override suspend fun list(path: String): AtlasResult<List<RemoteFileEntry>> =
        withClient { client ->
            val safePath = requireWorkspacePath(client, path)
            @Suppress("UNCHECKED_CAST")
            val entries = client.ls(safePath) as java.util.Vector<SFTPv3DirectoryEntry>
            entries.asSequence()
                .filter { it.filename != "." && it.filename != ".." }
                .map { entry ->
                    val attrs = entry.attributes
                    RemoteFileEntry(
                        path = SftpPath.child(safePath, entry.filename),
                        name = entry.filename,
                        directory = attrs?.isDirectory ?: false,
                        sizeBytes = attrs?.size ?: 0L,
                        modifiedEpochMillis = (attrs?.mtime ?: 0L) * 1000L,
                    )
                }
                .sortedWith(compareBy<RemoteFileEntry> { !it.directory }.thenBy { it.name.lowercase() })
                .toList()
        }

    override suspend fun readText(path: String): AtlasResult<RemoteTextDocument> =
        withClient { client ->
            val safePath = requireWorkspacePath(client, path)
            val attrs = client.stat(safePath)
            val size = attrs.size ?: 0L
            if (size > maxTextBytes) throw FileTooLargeException(size, maxTextBytes)

            val bytes = readAll(client, safePath, size)
            val snapshot = RemoteFileSnapshot(
                path = safePath,
                sizeBytes = bytes.size.toLong(),
                modifiedEpochMillis = (attrs.mtime ?: 0L) * 1000L,
                contentHash = sha256Hex(bytes),
            )
            RemoteTextDocument(snapshot = snapshot, text = bytes.toString(Charsets.UTF_8))
        }

    override suspend fun writeTextAtomic(
        request: AtomicTextWriteRequest,
    ): AtlasResult<RemoteFileSnapshot> =
        withClient { client ->
            val safePath = requireWorkspacePath(client, request.path)
            val safeExpected = request.expectedSnapshot.copy(path = safePath)
            verifyExpectedSnapshot(client, safeExpected)

            val payload = request.text.toByteArray(Charsets.UTF_8)
            val nonce = sha256Hex(
                (safePath + ":" + request.expectedSnapshot.modifiedEpochMillis + ":" + payload.size)
                    .toByteArray(Charsets.UTF_8)
            ).take(16)
            val temporary = SftpPath.temporaryFor(safePath, nonce)

            var tempCreated = false
            try {
                val handle = client.createFileTruncate(temporary)
                tempCreated = true
                try {
                    client.write(handle, 0L, payload, 0, payload.size)
                } finally {
                    client.closeFile(handle)
                }

                client.mv(temporary, safePath)
                tempCreated = false

                val attrs = client.stat(safePath)
                RemoteFileSnapshot(
                    path = safePath,
                    sizeBytes = attrs.size ?: payload.size.toLong(),
                    modifiedEpochMillis = (attrs.mtime ?: 0L) * 1000L,
                    contentHash = sha256Hex(payload),
                )
            } finally {
                if (tempCreated) runCatching { client.rm(temporary) }
            }
        }

    private fun requireWorkspacePath(client: SFTPv3Client, path: String): String {
        val root = client.canonicalPath(profile.workspaceRoot).trimEnd('/').ifBlank { "/" }
        val canonical = client.canonicalPath(path).trimEnd('/').ifBlank { "/" }
        val within = root == "/" || canonical == root || canonical.startsWith("$root/")
        if (!within) throw WorkspaceBoundaryException(canonical, root)
        return canonical
    }

    private fun verifyExpectedSnapshot(client: SFTPv3Client, expected: RemoteFileSnapshot) {
        val attrs = client.stat(expected.path)
        val currentSize = attrs.size ?: 0L
        val currentMtime = (attrs.mtime ?: 0L) * 1000L
        if (currentSize != expected.sizeBytes || currentMtime != expected.modifiedEpochMillis) {
            throw RemoteConflictException()
        }

        val expectedHash = expected.contentHash
        if (expectedHash != null) {
            if (currentSize > maxTextBytes) throw FileTooLargeException(currentSize, maxTextBytes)
            val current = readAll(client, expected.path, currentSize)
            if (sha256Hex(current) != expectedHash) throw RemoteConflictException()
        }
    }

    private fun readAll(client: SFTPv3Client, path: String, expectedSize: Long): ByteArray {
        val out = ByteArrayOutputStream(expectedSize.coerceAtMost(Int.MAX_VALUE.toLong()).toInt())
        val handle = client.openFileRO(path)
        try {
            val buffer = ByteArray(32 * 1024)
            var offset = 0L
            while (true) {
                val count = client.read(handle, offset, buffer, 0, buffer.size)
                if (count < 0) break
                if (count == 0) continue
                out.write(buffer, 0, count)
                offset += count
                if (offset > maxTextBytes) throw FileTooLargeException(offset, maxTextBytes)
            }
            return out.toByteArray()
        } finally {
            client.closeFile(handle)
        }
    }

    private suspend fun <T> withClient(block: (SFTPv3Client) -> T): AtlasResult<T> {
        val credential = when (val loaded = credentials.loadSshCredential(profile.id)) {
            is AtlasResult.Success -> loaded.value
            is AtlasResult.Failure -> return loaded
        }

        return try {
            when (val opened = openClient(credential)) {
                is AtlasResult.Failure -> opened
                is AtlasResult.Success -> {
                    val connected = opened.value
                    try {
                        AtlasResult.Success(block(connected.client))
                    } catch (err: WorkspaceBoundaryException) {
                        failure(
                            "file_outside_workspace",
                            ErrorDomain.VALIDATION,
                            "error_file_outside_workspace",
                            detail = "${err.path} outside ${err.root}",
                            retryable = false,
                        )
                    } catch (_: RemoteConflictException) {
                        failure(
                            "file_changed_remotely",
                            ErrorDomain.FILE_CONFLICT,
                            "error_file_changed_remotely",
                            retryable = false,
                        )
                    } catch (err: FileTooLargeException) {
                        failure(
                            "file_too_large",
                            ErrorDomain.VALIDATION,
                            "error_file_too_large",
                            detail = "${err.actualBytes}>${err.limitBytes}",
                            retryable = false,
                        )
                    } catch (err: Exception) {
                        failure(
                            "sftp_operation_failed",
                            ErrorDomain.SFTP,
                            "error_sftp_operation_failed",
                            detail = err.javaClass.simpleName + ": " + (err.message ?: "operation"),
                            retryable = false,
                        )
                    } finally {
                        runCatching { connected.client.close() }
                        runCatching { connected.connection.close() }
                    }
                }
            }
        } finally {
            wipeCredential(credential)
        }
    }

    private fun openClient(credential: SshCredential): AtlasResult<ConnectedSftp> {
        var lastTransportFailure: AtlasResult.Failure? = null
        val endpoints = profile.sshEndpoints()

        for ((index, endpoint) in endpoints.withIndex()) {
            var connection: Connection? = null
            var rejectedObservation: HostKeyObservation? = null
            try {
                val conn = Connection(endpoint.host, endpoint.port)
                connection = conn
                val verifier = ServerHostKeyVerifier { host, port, algorithm, key ->
                    val observation = HostKeyObservation(
                        host = host,
                        port = port,
                        algorithm = algorithm,
                        fingerprint = fingerprint(key),
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
                    runCatching { conn.close() }
                    return failure(
                        "sftp_auth_failed",
                        ErrorDomain.AUTH,
                        "error_sftp_auth_failed",
                    )
                }

                val sftp = SFTPv3Client(conn)
                sftp.setCharset("UTF-8")
                return AtlasResult.Success(ConnectedSftp(conn, sftp))
            } catch (err: Exception) {
                runCatching { connection?.close() }
                val blocked = rejectedObservation
                if (blocked != null) {
                    return failure(
                        "sftp_host_key_blocked",
                        ErrorDomain.TRUST,
                        "error_sftp_host_key_blocked",
                        detail = "${blocked.host}:${blocked.port} ${blocked.algorithm} ${blocked.fingerprint}",
                        retryable = false,
                    )
                }

                val classified = TransportFailureClassifier.classify(err)
                val failure = failure<ConnectedSftp>(
                    classified.code,
                    classified.domain,
                    "error_sftp_connect_failed",
                    detail = "${endpoint.label} ${endpoint.host}:${endpoint.port} • " +
                        err.javaClass.simpleName + ": " + (err.message ?: "transport"),
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
            ?: failure(
                "network_transport_failed",
                ErrorDomain.NETWORK,
                "error_sftp_connect_failed",
            )
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

    private fun fingerprint(serverHostKey: ByteArray): String {
        val digest = MessageDigest.getInstance("SHA-256").digest(serverHostKey)
        return "SHA256:" + Base64.getEncoder().withoutPadding().encodeToString(digest)
    }

    private fun sha256Hex(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256")
            .digest(bytes)
            .joinToString("") { "%02x".format(it) }

    private fun <T> failure(
        code: String,
        domain: ErrorDomain,
        messageKey: String,
        detail: String? = null,
        retryable: Boolean = false,
    ): AtlasResult<T> = AtlasResult.Failure(
        AtlasError(code, domain, messageKey, detail, retryable)
    )

    private data class ConnectedSftp(
        val connection: Connection,
        val client: SFTPv3Client,
    )

    private class WorkspaceBoundaryException(
        val path: String,
        val root: String,
    ) : RuntimeException()

    private class RemoteConflictException : RuntimeException()
    private class FileTooLargeException(
        val actualBytes: Long,
        val limitBytes: Long,
    ) : RuntimeException()
}
