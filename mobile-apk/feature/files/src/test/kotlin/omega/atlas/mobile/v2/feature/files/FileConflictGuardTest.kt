package omega.atlas.mobile.v2.feature.files

import omega.atlas.mobile.v2.core.model.RemoteFileSnapshot
import org.junit.Assert.assertEquals
import org.junit.Test

class FileConflictGuardTest {
    private val original = RemoteFileSnapshot(
        path = "/repo/main.py",
        sizeBytes = 100,
        modifiedEpochMillis = 1000,
        contentHash = "abc",
    )

    @Test
    fun sameHashIsSafeEvenWhenMetadataResolutionDiffers() {
        val current = original.copy(modifiedEpochMillis = 1001)
        assertEquals(FileConflictDecision.SAFE_TO_WRITE, FileConflictGuard.compare(original, current))
    }

    @Test
    fun changedHashBlocksWrite() {
        val current = original.copy(contentHash = "def")
        assertEquals(FileConflictDecision.REMOTE_CHANGED, FileConflictGuard.compare(original, current))
    }

    @Test
    fun metadataFallbackBlocksChangedRemoteFile() {
        val expected = original.copy(contentHash = null)
        val current = expected.copy(sizeBytes = 101)
        assertEquals(FileConflictDecision.REMOTE_CHANGED, FileConflictGuard.compare(expected, current))
    }
}
