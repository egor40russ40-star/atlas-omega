package omega.atlas.mobile.v2.feature.connections

import omega.atlas.mobile.v2.core.model.ConnectionProfile
import omega.atlas.mobile.v2.core.model.TrustState
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ConnectionLaunchPolicyTest {
    private fun profile(
        autoConnect: Boolean,
        trustState: TrustState,
    ) = ConnectionProfile(
        id = "test",
        title = "Test",
        host = "host",
        username = "user",
        autoConnect = autoConnect,
        trustState = trustState,
    )

    @Test
    fun trustedProfileMayAutoConnect() {
        assertTrue(ConnectionLaunchPolicy.canAutoConnect(profile(true, TrustState.TRUSTED)))
    }

    @Test
    fun pendingTrustNeverAutoConnects() {
        assertFalse(ConnectionLaunchPolicy.canAutoConnect(profile(true, TrustState.PENDING)))
    }

    @Test
    fun disabledAutoConnectStaysDisabled() {
        assertFalse(ConnectionLaunchPolicy.canAutoConnect(profile(false, TrustState.TRUSTED)))
    }
}
