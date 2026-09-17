package omega.atlas.mobile.v2.storage.local

import omega.atlas.mobile.v2.core.security.SshCredential
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class CredentialCodecTest {
    @Test
    fun passwordRoundTripPreservesCharacters() {
        val source = SshCredential.Password("пароль-123".toCharArray())
        val decoded = CredentialCodec.decode(CredentialCodec.encode(source))
        assertTrue(decoded is SshCredential.Password)
        assertArrayEquals(source.value, (decoded as SshCredential.Password).value)
    }

    @Test
    fun privateKeyRoundTripSupportsOptionalPassphrase() {
        val source = SshCredential.PrivateKey(
            pem = "-----BEGIN KEY-----\nabc\n-----END KEY-----".toCharArray(),
            passphrase = null,
        )
        val decoded = CredentialCodec.decode(CredentialCodec.encode(source))
        assertTrue(decoded is SshCredential.PrivateKey)
        decoded as SshCredential.PrivateKey
        assertArrayEquals(source.pem, decoded.pem)
        assertNull(decoded.passphrase)
    }
}
