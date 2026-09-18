package omega.atlas.mobile.v2.feature.atlas

import java.net.URI
import omega.atlas.mobile.v2.core.result.AtlasResult

data class GatewayVersion(
    val product: String,
    val version: String,
    val apiVersion: String,
    val mode: String,
    val identityMode: String,
    val liveTradingAuthority: String,
) {
    val liveTradingAuthorityAbsent: Boolean
        get() = liveTradingAuthority.equals("ABSENT", ignoreCase = true)
}

interface GatewayStatusPort {
    suspend fun version(baseUrl: String): AtlasResult<GatewayVersion>
}

object GatewayEndpointPolicy {
    fun normalizeHttpsBaseUrl(raw: String): String {
        val normalized = raw.trim().trimEnd('/')
        val uri = URI(normalized)
        require(uri.scheme.equals("https", ignoreCase = true)) { "Gateway must use HTTPS" }
        require(!uri.host.isNullOrBlank()) { "Gateway host is required" }
        require(uri.userInfo == null) { "Gateway URL must not contain credentials" }
        return normalized
    }

    fun versionUrl(baseUrl: String): String =
        normalizeHttpsBaseUrl(baseUrl) + "/version"
}
