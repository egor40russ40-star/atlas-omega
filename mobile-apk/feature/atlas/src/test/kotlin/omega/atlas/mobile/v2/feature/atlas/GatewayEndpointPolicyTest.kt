package omega.atlas.mobile.v2.feature.atlas

import org.junit.Assert.assertEquals
import org.junit.Test

class GatewayEndpointPolicyTest {
    @Test
    fun normalizesHttpsBaseUrl() {
        assertEquals(
            "https://atlas.example",
            GatewayEndpointPolicy.normalizeHttpsBaseUrl(" https://atlas.example/ "),
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsHttp() {
        GatewayEndpointPolicy.normalizeHttpsBaseUrl("http://atlas.example")
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsCredentialsInUrl() {
        GatewayEndpointPolicy.normalizeHttpsBaseUrl("https://user:pass@atlas.example")
    }
}
