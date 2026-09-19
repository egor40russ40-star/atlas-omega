package omega.atlas.mobile.v2.core.result

import java.net.ConnectException
import java.net.NoRouteToHostException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import javax.net.ssl.SSLException

data class TransportFailureClassification(
    val code: String,
    val domain: ErrorDomain,
    val retryable: Boolean,
)

object TransportFailureClassifier {
    fun classify(error: Throwable): TransportFailureClassification {
        val chain = generateSequence(error) { it.cause }.toList()
        val message = chain.joinToString(" | ") { it.message.orEmpty() }.lowercase()

        return when {
            chain.any { it is UnknownHostException } ||
                "could not resolve hostname" in message ||
                "no address associated with hostname" in message ->
                failure("network_dns_failed")

            chain.any { it is NoRouteToHostException } ||
                "no route to host" in message ||
                "network is unreachable" in message ->
                failure("network_route_unavailable")

            chain.any { it is SocketTimeoutException } ||
                "timed out" in message ||
                "timeout" in message ->
                failure("network_timeout")

            chain.any { it is ConnectException } &&
                ("refused" in message || "connection refused" in message) ->
                failure("network_connection_refused")

            chain.any { it is SSLException } ||
                "ssl" in message ||
                "tls" in message ||
                "certificate" in message ->
                TransportFailureClassification(
                    code = "network_tls_failed",
                    domain = ErrorDomain.NETWORK,
                    retryable = false,
                )

            "connection closed by remote host" in message ||
                "kex_exchange_identification" in message ||
                "closed before" in message ||
                "connection reset" in message ||
                "broken pipe" in message ->
                failure("network_remote_closed")

            else -> failure("network_transport_failed")
        }
    }

    private fun failure(code: String) = TransportFailureClassification(
        code = code,
        domain = ErrorDomain.NETWORK,
        retryable = true,
    )
}
