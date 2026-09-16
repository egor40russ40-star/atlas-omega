package omega.atlas.mobile

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AtlasConfigTest {
    @Test
    fun gatewayRequiresHttps() {
        assertTrue(AtlasConfig.isAllowedGateway("https://tinvest-robot.tailf87948.ts.net"))
        assertFalse(AtlasConfig.isAllowedGateway("http://tinvest-robot.tailf87948.ts.net"))
        assertFalse(AtlasConfig.isAllowedGateway("http://127.0.0.1:8787"))
    }

    @Test
    fun terminalControlSequencesAreCorrect() {
        assertArrayEquals(byteArrayOf(3), TerminalKeys.ctrl('C'))
        assertArrayEquals(byteArrayOf(4), TerminalKeys.ctrl('D'))
        assertArrayEquals(byteArrayOf(27), TerminalKeys.esc)
    }

    @Test
    fun tradingAuthorityRemainsDisabled() {
        assertFalse(AtlasConfig.LIVE_TRADING_ENABLED)
        assertTrue(AtlasConfig.RESEARCH_ONLY)
    }
}
