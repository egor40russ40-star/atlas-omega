package omega.atlas.mobile.v2.core.result

import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import javax.net.ssl.SSLHandshakeException
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class TransportFailureClassifierTest {
    @Test
    fun classifiesDnsFailure() {
        val x = TransportFailureClassifier.classify(
            UnknownHostException("No address associated with hostname")
        )
        assertEquals("network_dns_failed", x.code)
        assertEquals(ErrorDomain.NETWORK, x.domain)
        assertTrue(x.retryable)
    }

    @Test
    fun classifiesTimeout() {
        val x = TransportFailureClassifier.classify(SocketTimeoutException("connect timed out"))
        assertEquals("network_timeout", x.code)
    }

    @Test
    fun classifiesRefusedConnection() {
        val x = TransportFailureClassifier.classify(ConnectException("Connection refused"))
        assertEquals("network_connection_refused", x.code)
    }

    @Test
    fun classifiesRemoteCloseFromSshText() {
        val x = TransportFailureClassifier.classify(
            IllegalStateException("kex_exchange_identification: Connection closed by remote host")
        )
        assertEquals("network_remote_closed", x.code)
    }

    @Test
    fun tlsFailureIsNotBlindlyRetried() {
        val x = TransportFailureClassifier.classify(SSLHandshakeException("certificate mismatch"))
        assertEquals("network_tls_failed", x.code)
        assertFalse(x.retryable)
    }
}
