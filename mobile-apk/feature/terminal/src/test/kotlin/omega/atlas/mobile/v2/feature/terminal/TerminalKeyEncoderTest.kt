package omega.atlas.mobile.v2.feature.terminal

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class TerminalKeyEncoderTest {
    @Test
    fun arrowsUseAnsiSequences() {
        assertArrayEquals("\u001B[A".encodeToByteArray(), TerminalKeyEncoder.encode(TerminalKey.UP))
        assertArrayEquals("\u001B[D".encodeToByteArray(), TerminalKeyEncoder.encode(TerminalKey.LEFT))
    }

    @Test
    fun controlCUsesEtX() {
        assertArrayEquals(byteArrayOf(0x03), TerminalKeyEncoder.ctrl('C'))
    }

    @Test
    fun multilinePasteRequiresConfirmation() {
        assertTrue(PasteSafety.requiresConfirmation("echo one\necho two"))
        assertFalse(PasteSafety.requiresConfirmation("git status"))
    }
}
