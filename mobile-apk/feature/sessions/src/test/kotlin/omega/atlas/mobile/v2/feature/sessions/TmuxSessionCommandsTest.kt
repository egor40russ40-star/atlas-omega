package omega.atlas.mobile.v2.feature.sessions

import org.junit.Assert.assertEquals
import org.junit.Test

class TmuxSessionCommandsTest {
    @Test
    fun attachCommandIsIdempotentAndReusesExistingSession() {
        assertEquals(
            "exec tmux new-session -A -s atlas-mobile-main\r",
            TmuxSessionCommands.attachOrCreate("atlas-mobile-main").decodeToString(),
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun unsafeNameIsRejectedBeforeShellWrite() {
        TmuxSessionCommands.attachOrCreate("atlas;shutdown")
    }
}
