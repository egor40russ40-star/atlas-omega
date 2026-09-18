package omega.atlas.mobile.v2.transport.gateway

import java.net.URL
import javax.net.ssl.HttpsURLConnection
import org.json.JSONObject
import omega.atlas.mobile.v2.core.result.AtlasError
import omega.atlas.mobile.v2.core.result.AtlasResult
import omega.atlas.mobile.v2.core.result.ErrorDomain
import omega.atlas.mobile.v2.feature.atlas.GatewayEndpointPolicy
import omega.atlas.mobile.v2.feature.atlas.GatewayStatusPort
import omega.atlas.mobile.v2.feature.atlas.GatewayVersion

class HttpsGatewayStatusClient(
    private val connectTimeoutMillis: Int = 8_000,
    private val readTimeoutMillis: Int = 8_000,
    private val maxResponseBytes: Int = 256 * 1024,
) : GatewayStatusPort {

    override suspend fun version(baseUrl: String): AtlasResult<GatewayVersion> {
        val endpoint = try {
            GatewayEndpointPolicy.versionUrl(baseUrl)
        } catch (e: Exception) {
            return failure("gateway_url_invalid", ErrorDomain.VALIDATION, e.message, false)
        }

        var connection: HttpsURLConnection? = null
        return try {
            val conn = (URL(endpoint).openConnection() as HttpsURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = connectTimeoutMillis
                readTimeout = readTimeoutMillis
                instanceFollowRedirects = false
                setRequestProperty("Accept", "application/json")
                setRequestProperty("User-Agent", "ATLAS-Mobile-2/0.2.0")
            }
            connection = conn
            val code = conn.responseCode
            if (code != 200) {
                return failure(
                    "gateway_http_error",
                    ErrorDomain.GATEWAY,
                    "HTTP $code",
                    code in 500..599,
                )
            }

            val body = conn.inputStream.use { input ->
                val buffer = ByteArray(16 * 1024)
                val out = java.io.ByteArrayOutputStream()
                while (true) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    if (count == 0) continue
                    if (out.size() + count > maxResponseBytes) {
                        return failure(
                            "gateway_response_too_large",
                            ErrorDomain.GATEWAY,
                            "Response exceeds $maxResponseBytes bytes",
                            false,
                        )
                    }
                    out.write(buffer, 0, count)
                }
                out.toString(Charsets.UTF_8.name())
            }

            val json = JSONObject(body)
            val result = GatewayVersion(
                product = required(json, "product"),
                version = required(json, "version"),
                apiVersion = required(json, "api_version"),
                mode = required(json, "mode"),
                identityMode = required(json, "identity_mode"),
                liveTradingAuthority = required(json, "live_trading_authority"),
            )
            AtlasResult.Success(result)
        } catch (e: Exception) {
            failure(
                "gateway_request_failed",
                ErrorDomain.NETWORK,
                e.javaClass.simpleName + ": " + (e.message ?: "network"),
                true,
            )
        } finally {
            connection?.disconnect()
        }
    }

    private fun required(json: JSONObject, key: String): String {
        val value = json.optString(key, "").trim()
        require(value.isNotEmpty()) { "Missing $key" }
        return value
    }

    private fun <T> failure(
        code: String,
        domain: ErrorDomain,
        detail: String?,
        retryable: Boolean,
    ): AtlasResult<T> = AtlasResult.Failure(
        AtlasError(
            code = code,
            domain = domain,
            userMessageKey = "error_gateway_status",
            technicalDetail = detail,
            retryable = retryable,
        )
    )
}
