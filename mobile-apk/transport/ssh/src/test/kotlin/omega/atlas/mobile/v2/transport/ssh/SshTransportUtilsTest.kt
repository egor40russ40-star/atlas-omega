package omega.atlas.mobile.v2.transport.ssh

import org.junit.Assert.assertEquals
import org.junit.Test

class SshTransportUtilsTest {
    @Test
    fun fingerprintIsStableSha256Base64() {
        assertEquals(
            "SHA256:ungWv48Bz+pBQUDeXa4iI7ADYaOWF3qctBD/YfIAFa0",
            SshTransportUtils.fingerprint("atlas".encodeToByteArray()),
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun tmuxSessionRejectsShellCharacters() {
        SshTransportUtils.requireSafeTmuxSessionName("atlas;rm")
    }

    @Test
    fun tmuxSessionAcceptsGeneratedName() {
        assertEquals(
            "atlas-mobile-main_01",
            SshTransportUtils.requireSafeTmuxSessionName("atlas-mobile-main_01"),
        )
    }
}
