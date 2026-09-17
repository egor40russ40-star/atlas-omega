package omega.atlas.mobile.v2.core.security

import omega.atlas.mobile.v2.core.result.AtlasResult

sealed interface SshCredential {
    data object None : SshCredential
    class Password(val value: CharArray) : SshCredential
    class PrivateKey(
        val pem: CharArray,
        val passphrase: CharArray? = null,
    ) : SshCredential
}

interface CredentialVault {
    suspend fun loadSshCredential(connectionProfileId: String): AtlasResult<SshCredential>
}

interface MutableCredentialVault : CredentialVault {
    suspend fun saveSshCredential(
        connectionProfileId: String,
        credential: SshCredential,
    ): AtlasResult<Unit>

    suspend fun removeSshCredential(connectionProfileId: String): AtlasResult<Unit>
}

enum class HostKeyDecision {
    TRUSTED,
    UNSEEN,
    CHANGED,
}

data class HostKeyObservation(
    val host: String,
    val port: Int,
    val algorithm: String,
    val fingerprint: String,
)

interface HostKeyTrustPolicy {
    fun evaluate(observation: HostKeyObservation): HostKeyDecision
}

interface MutableHostKeyTrustPolicy : HostKeyTrustPolicy {
    fun pin(observation: HostKeyObservation)
    fun clear(host: String, port: Int)
}

interface HostKeyFingerprintStore {
    fun read(host: String, port: Int, algorithm: String): String?
    fun write(host: String, port: Int, algorithm: String, fingerprint: String)
    fun clear(host: String, port: Int)
}

class PinnedHostKeyTrustPolicy(
    private val store: HostKeyFingerprintStore,
) : MutableHostKeyTrustPolicy {
    override fun evaluate(observation: HostKeyObservation): HostKeyDecision {
        val pinned = store.read(observation.host, observation.port, observation.algorithm)
            ?: return HostKeyDecision.UNSEEN
        return if (pinned == observation.fingerprint) HostKeyDecision.TRUSTED else HostKeyDecision.CHANGED
    }

    override fun pin(observation: HostKeyObservation) {
        store.write(
            observation.host,
            observation.port,
            observation.algorithm,
            observation.fingerprint,
        )
    }

    override fun clear(host: String, port: Int) {
        store.clear(host, port)
    }
}
