package omega.atlas.mobile.v2.feature.git

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class GitActionPolicyTest {
    @Test
    fun conflictCannotBeStagedBlindly() {
        assertFalse(
            GitActionPolicy.canStage(
                GitFileChange("src/Main.kt", GitChangeKind.CONFLICT, staged = false),
            ),
        )
    }

    @Test
    fun normalChangeCanBeStaged() {
        assertTrue(
            GitActionPolicy.canStage(
                GitFileChange("src/Main.kt", GitChangeKind.MODIFIED, staged = false),
            ),
        )
    }

    @Test
    fun commitMessageIsTrimmed() {
        assertEquals("fix terminal", GitActionPolicy.requireCommitMessage("  fix terminal  "))
    }

    @Test(expected = IllegalArgumentException::class)
    fun blankCommitMessageIsRejected() {
        GitActionPolicy.requireCommitMessage("   ")
    }

    @Test
    fun destructiveGitActionsStayDisabled() {
        assertFalse(GitActionPolicy.supportsDestructiveReset())
        assertFalse(GitActionPolicy.supportsForcePush())
    }
}
