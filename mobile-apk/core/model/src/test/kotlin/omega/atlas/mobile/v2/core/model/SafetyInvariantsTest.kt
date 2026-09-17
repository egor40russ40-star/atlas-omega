package omega.atlas.mobile.v2.core.model

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class SafetyInvariantsTest {
    @Test
    fun tradingAuthorityNeverAppearsInMobileCore() {
        assertFalse(SafetyInvariants.liveTradingEnabled)
        assertFalse(SafetyInvariants.liveTradingAuthorityPresent)
        assertFalse(SafetyInvariants.autoTrustNewDevice)
        assertTrue(SafetyInvariants.researchOnly)
    }
}
