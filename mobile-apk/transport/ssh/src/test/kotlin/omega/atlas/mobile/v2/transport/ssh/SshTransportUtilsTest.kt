package omega.atlas.mobile.v2.transport.ssh

import org.junit.Assert.assertEquals
import org.junit.Test

class SshTransportUtilsTest {
    @Test
    fun fingerprintIsStableSha256Base64() {
        assertEquals(
            "SHA256:fIJgJQCFeqbtDPOMTD5OxkW9yqgsALkVXrCL4QDHeKk",
            SshTransportUtils.fingerprint("atlas".encodeToByteArray()),
        )
    }

    @Test
    fun fingerprintMatchesIndependentSha256HexVector() {
        val actual = SshTransportUtils.fingerprint("atlas".encodeToByteArray())
        assertEquals("SHA256:fIJgJQCFeqbtDPOMTD5OxkW9yqgsALkVXrCL4QDHeKk", actual)
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
