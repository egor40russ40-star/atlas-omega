package omega.atlas.mobile.v2.testing.fakes

import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.security.CredentialVault
import omega.atlas.mobile.v2.core.security.HostKeyFingerprintStore
import omega.atlas.mobile.v2.core.security.SshCredential

class InMemoryHostKeyFingerprintStore : HostKeyFingerprintStore {
    private val values = mutableMapOf<String, String>()

    override fun read(host: String, port: Int, algorithm: String): String? =
        values[key(host, port, algorithm)]

    override fun write(host: String, port: Int, algorithm: String, fingerprint: String) {
        values[key(host, port, algorithm)] = fingerprint
    }

    override fun clear(host: String, port: Int) {
        val prefix = "$host:$port:"
        values.keys.filter { it.startsWith(prefix) }.forEach(values::remove)
    }

    private fun key(host: String, port: Int, algorithm: String) = "$host:$port:$algorithm"
}

class FakeCredentialVault(
    private val credentials: Map<String, SshCredential> = emptyMap(),
) : CredentialVault {
    override suspend fun loadSshCredential(connectionProfileId: String): AtlasResult<SshCredential> =
        AtlasResult.Success(credentials[connectionProfileId] ?: SshCredential.None)
}
